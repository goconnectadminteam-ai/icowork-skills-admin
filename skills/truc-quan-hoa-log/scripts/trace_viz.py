#!/usr/bin/env python3
"""Vẽ timeline từ file log Langfuse (trace-*.json) thành HTML + PNG và in các dấu hiệu lỗi.

Chỉ dùng thư viện chuẩn của Python 3. PNG cần Google Chrome / Microsoft Edge (không có thì chỉ ra HTML).

  python3 trace_viz.py INPUT.json [--out DIR] [--tz 7] [--no-png]

In ra stdout một bản tóm tắt dạng văn bản (các bước, dấu hiệu, chuỗi nguyên nhân suy ra từ luật)
để model đọc và viết phần diễn giải. Không in nội dung dài của log.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---- ngưỡng phát hiện (chỉnh ở đây) -------------------------------------------------
COMPACT_DROP = 0.40      # token vào giảm >= 40% so với lượt sinh trước => nghi nén ngữ cảnh
COMPACT_MIN_PREV = 20000  # chỉ xét khi lượt trước >= 20k token
BIG_CONTEXT = 50000      # cảnh báo ngữ cảnh lớn
SLOW_GEN_S = 20.0        # lượt sinh chậm
REASONING_CAP = 16384    # chạm trần reasoning thường là cái trần cấu hình của model
REPEAT_TOOL = 6          # gọi cùng một tool >= N lần liên tiếp thì gộp + ghi nhận
LOOP_RATIO = 0.30        # tỉ lệ câu lặp trong phần suy nghĩ để coi là vòng lặp


def load(v):
    """Giải JSON lồng nhiều lớp chuỗi (Langfuse hay lưu JSON trong chuỗi)."""
    for _ in range(4):
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except ValueError:
                break
        else:
            break
    return v


def parse_time(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def span_s(o):
    """Thời lượng (giây) tính từ startTime/endTime; trường latency lúc là giây lúc là ms nên không dùng."""
    a, b = parse_time(o.get('startTime')), parse_time(o.get('endTime'))
    return (b - a).total_seconds() if a and b else None


def fmt_tok(n):
    n = n or 0
    return f'{n / 1000:.0f}k' if n >= 10000 else (f'{n / 1000:.1f}k' if n >= 1000 else str(n))


def fmt_dur(s):
    if s is None:
        return ''
    return f'{s:.0f} giây' if s >= 10 else (f'{s:.1f} giây' if s >= 1 else f'{s * 1000:.0f} ms')


def trunc(s, n):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    return s if len(s) <= n else s[:n - 1] + '…'


# ---- đọc log -------------------------------------------------------------------------
def read_trace(path):
    try:
        raw = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        raise SystemExit(f'Không đọc được "{path}" như file JSON Langfuse ({type(e).__name__}).')
    if isinstance(raw, dict) and 'trace' in raw:
        trace, obs = raw['trace'], raw.get('observations') or raw['trace'].get('observations') or []
    elif isinstance(raw, dict) and 'observations' in raw:
        trace, obs = raw, raw['observations']
    else:
        raise SystemExit('Không nhận ra định dạng: cần file xuất từ Langfuse có khoá "trace" và "observations".')
    trace = dict(trace)
    trace['_input'] = load(trace.get('input'))
    trace['_output'] = load(trace.get('output'))
    trace['_meta'] = load(trace.get('metadata')) or {}
    return trace, obs


def user_request(trace):
    """Lấy yêu cầu người dùng: iWork nhét sau nhãn 'User request:'; không có thì lấy đầu tin nhắn."""
    inp = trace['_input']
    text = ''
    if isinstance(inp, list):
        for m in inp:
            c = m.get('content') if isinstance(m, dict) else None
            if isinstance(c, list):
                text += ' '.join(p.get('text', '') for p in c if isinstance(p, dict))
            elif isinstance(c, str):
                text += c
    elif isinstance(inp, dict):
        for m in inp.get('messages') or []:
            if isinstance(m, dict) and m.get('role') == 'user':
                c = m.get('content')
                text = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
    m = re.search(r'User request:\s*(.+?)(?:\n\s*---\n|IWORK_DATA_\S+_END|\Z)', text, re.S)
    return trunc(m.group(1) if m else text, 400)


def final_output(trace):
    """(văn bản trả lời cuối, danh sách tool_call chưa chạy, văn bản suy nghĩ)"""
    out = trace['_output']
    if isinstance(out, list) and out and isinstance(out[0], dict):
        o = out[0]
        content = o.get('content') or ''
        thinking = ' '.join(t.get('content', '') for t in (o.get('thinking') or []) if isinstance(t, dict))
        return (content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)), (o.get('tool_calls') or []), thinking
    if isinstance(out, str):
        return out, [], ''
    return '', [], ''


# ---- dựng các bước ---------------------------------------------------------------------
def build_steps(trace, obs):
    t0 = min(parse_time(o['startTime']) for o in obs) if obs else parse_time(trace.get('timestamp'))
    obs = sorted(obs, key=lambda o: o['startTime'])
    steps = []   # mỗi bước: dict(kind, t, dur, title, detail, level, tokens...)
    gens = [o for o in obs if o['type'] == 'GENERATION']
    tools = [o for o in obs if o['type'] == 'TOOL']
    prev_in = None
    for g in gens:
        u = g.get('usageDetails') or {}
        st = {'kind': 'gen', 't': parse_time(g['startTime']), 'dur': span_s(g), 'in': u.get('input') or 0,
              'out': u.get('output') or 0, 'reasoning': u.get('reasoning') or 0, 'id': g['id'], 'model': g.get('model'),
              'prev_in': prev_in}
        prev_in = st['in'] or prev_in
        steps.append(st)
    # gom tool theo lượt sinh cha, rồi gộp các lần gọi liên tiếp cùng tên
    by_parent = {}
    for t in tools:
        by_parent.setdefault(t.get('parentObservationId'), []).append(t)
    for pid, ts in by_parent.items():
        ts.sort(key=lambda o: o['startTime'])
        run = []
        for t in ts + [None]:
            if run and (t is None or t['name'] != run[0]['name'] or t['level'] == 'ERROR' or run[0]['level'] == 'ERROR'):
                a, b = parse_time(run[0]['startTime']), max(parse_time(x['endTime'] or x['startTime']) for x in run)
                steps.append({'kind': 'tool', 'name': run[0]['name'], 'n': len(run), 't': a, 'dur': (b - a).total_seconds(),
                              'error': [x for x in run if x['level'] == 'ERROR'], 'parent': pid})
                run = []
            if t is not None:
                run.append(t)
    steps.sort(key=lambda s: s['t'])
    return t0, steps


def merge_tool_batches(steps):
    """Một lượt sinh + các tool nó gọi => một thẻ. Trả về danh sách thẻ để vẽ."""
    cards, i = [], 0
    while i < len(steps):
        s = steps[i]
        if s['kind'] == 'gen':
            kids = []
            j = i + 1
            while j < len(steps) and steps[j]['kind'] == 'tool' and steps[j]['parent'] == s['id']:
                kids.append(steps[j])
                j += 1
            cards.append({'gen': s, 'tools': kids})
            i = j
        else:
            cards.append({'gen': None, 'tools': [s]})
            i += 1
    return cards


# ---- phát hiện dấu hiệu ------------------------------------------------------------------
def detect(trace, obs, steps, thinking, content, pending_calls):
    f = []   # dict(id, level, t, title, detail)
    gens = [s for s in steps if s['kind'] == 'gen']
    for g in gens:
        if g['prev_in'] and g['prev_in'] >= COMPACT_MIN_PREV and g['in'] <= g['prev_in'] * (1 - COMPACT_DROP):
            f.append({'id': 'compaction', 'level': 'warn', 't': g['t'],
                      'title': f'Ngữ cảnh bị nén (compaction) {fmt_tok(g["prev_in"])} → {fmt_tok(g["in"])} token',
                      'detail': 'Token đầu vào của lượt sinh này giảm mạnh so với lượt trước: nhiều khả năng ngữ cảnh bị tóm tắt, agent mất phần dữ liệu chi tiết đã lấy và phải đọc/gọi lại.',
                      'gid': g['id']})
        if g['reasoning'] and g['reasoning'] >= REASONING_CAP * 0.99 and not g['out']:
            f.append({'id': 'reasoning_cap', 'level': 'err', 't': g['t'],
                      'title': f'Chạm trần suy nghĩ ({g["reasoning"]:,} token) mà không ra câu trả lời',
                      'detail': f'Model dùng hết ngân sách reasoning trong {fmt_dur(g["dur"])} và output = 0.', 'gid': g['id']})
        if g['dur'] and g['dur'] >= SLOW_GEN_S:
            f.append({'id': 'slow_gen', 'level': 'warn', 't': g['t'],
                      'title': f'Lượt suy nghĩ chậm {fmt_dur(g["dur"])}',
                      'detail': f'{fmt_tok(g["in"])} token vào, {fmt_tok(g["reasoning"])} reasoning, {g["out"]} token ra.', 'gid': g['id']})
    if gens:
        peak = max(gens, key=lambda g: g['in'])
        if peak['in'] >= BIG_CONTEXT:
            f.append({'id': 'big_context', 'level': 'warn', 't': peak['t'], 'title': f'Ngữ cảnh lớn: đỉnh {fmt_tok(peak["in"])} token',
                      'detail': 'Ngữ cảnh phình do kết quả tool lớn; dễ kích hoạt nén ngữ cảnh.', 'gid': peak['id']})
    for s in steps:
        if s['kind'] == 'tool':
            for e in s['error']:
                msg = e.get('statusMessage') or ''
                rej = 'rejected permission' in msg or 'permission' in msg.lower()
                f.append({'id': 'tool_rejected' if rej else 'tool_error', 'level': 'err', 't': parse_time(e['startTime']),
                          'title': f'Tool "{e["name"]}" ' + ('bị từ chối quyền' if rej else 'báo lỗi'), 'detail': trunc(msg, 300), 'tool': e['name']})
            if s['n'] >= REPEAT_TOOL:
                f.append({'id': 'repeat_tool', 'level': 'info', 't': s['t'], 'title': f'Gọi "{s["name"]}" {s["n"]} lần liên tiếp',
                          'detail': 'Nếu mỗi lần là một đối tượng khác nhau (nhóm, trang) thì bình thường; nếu cùng tham số thì là vòng lặp.'})
    # vòng lặp trong phần suy nghĩ: tỉ lệ câu lặp
    sents = [x.strip().lower() for x in re.split(r'(?<=[.!?])\s+|\n+', thinking) if len(x.strip()) > 30]
    if len(sents) >= 8:
        rep = 1 - len(set(sents)) / len(sents)
        if rep >= LOOP_RATIO:
            f.append({'id': 'think_loop', 'level': 'err', 't': gens[-1]['t'] if gens else None,
                      'title': f'Vòng lặp trong suy nghĩ: {rep:.0%} câu bị lặp lại',
                      'detail': 'Model nhắc đi nhắc lại cùng một ý, không tiến tới hành động hay câu trả lời.'})
    # kết thúc không có báo cáo
    answered = bool(re.sub(r'<next_actions>.*', '', content or '', flags=re.S).strip())
    if not answered:
        why = 'còn lệnh tool chưa chạy' if pending_calls else 'không có nội dung trả lời'
        f.append({'id': 'no_answer', 'level': 'err', 't': (steps[-1]['t'] if steps else None),
                  'title': 'Lượt chạy kết thúc mà không có báo cáo', 'detail': f'Output cuối: {why}. Trạng thái trace vẫn có thể hiện "thành công".'})
    return f


def explain(findings):
    """Chuỗi nguyên nhân suy ra từ luật (model có thể viết lại cho hay hơn)."""
    ids = [x['id'] for x in findings]
    chain = []
    if 'big_context' in ids or 'compaction' in ids:
        chain.append('Kết quả tool quá lớn làm ngữ cảnh phình lên' + (' rồi bị nén (compaction), agent mất dữ liệu đã lấy và phải đọc lại.' if 'compaction' in ids else '.'))
    if 'reasoning_cap' in ids or 'think_loop' in ids:
        chain.append('Model suy nghĩ quá dài/lặp ý và chạm trần reasoning nên không kịp trả lời.')
    if 'tool_rejected' in ids:
        t = next(x for x in findings if x['id'] == 'tool_rejected')
        chain.append(f'Agent chọn tool "{t.get("tool")}" nhưng chính sách quyền chặn (lượt chạy không có người duyệt nên bị từ chối tự động).')
    if 'tool_error' in ids:
        chain.append('Có tool trả lỗi, kiểm tra tham số gọi và thông báo lỗi ở thẻ đỏ.')
    if 'no_answer' in ids:
        chain.append('Vì vậy lượt kết thúc không có câu trả lời cho người dùng.')
    return chain


# ---- vẽ HTML ---------------------------------------------------------------------------------
CSS = """
*{box-sizing:border-box}body{margin:0;background:#fff;color:#1f2430;font:14px/1.5 system-ui,'Segoe UI',Roboto,Arial,sans-serif}
.wrap{max-width:980px;margin:0 auto;padding:28px 24px 40px}
h1{font-size:20px;margin:0 0 4px}.sub{color:#667085;font-size:13px;margin-bottom:16px}
.req{background:#f4f6fa;border-radius:8px;padding:10px 14px;margin-bottom:16px;color:#344054}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:22px}
.stat{border:1px solid #e4e7ec;border-radius:8px;padding:8px 14px;min-width:120px}.stat b{display:block;font-size:18px}.stat span{color:#667085;font-size:12px}
.tl{position:relative;margin-left:4px}
.row{display:grid;grid-template-columns:78px 20px 1fr;gap:0 8px;align-items:start;margin-bottom:12px}
.time{color:#667085;font-size:13px;text-align:right;padding-top:12px;font-variant-numeric:tabular-nums}
.rail{position:relative;align-self:stretch;display:flex;justify-content:center}
.rail:before{content:'';position:absolute;top:0;bottom:-12px;width:2px;background:#e4e7ec}
.row:last-child .rail:before{bottom:50%}
.dot{background:currentColor;position:relative;z-index:1;width:12px;height:12px;border-radius:50%;margin-top:15px;border:2px solid #fff;box-shadow:0 0 0 1px currentColor}
.card{border:1px solid #e4e7ec;border-radius:10px;padding:10px 14px;background:#fff}
.card h3{margin:0;font-size:15px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.card p{margin:3px 0 0;color:#475467;font-size:13px;word-break:break-word}
.meta{color:#667085;font-weight:400;font-size:12px}
.badge{font-size:11px;font-weight:600;padding:1px 8px;border-radius:999px}
.ok{color:#12805c}.badge.ok{background:#d9f2e6;color:#0b6b4a}
.warn{color:#b7791f}.card.warn{background:#fbe9bd;border-color:#f0c96a;color:#5b3d05}.card.warn p{color:#6b4a0c}.badge.warn{background:#f0c96a;color:#5b3d05}
.err{color:#b42318}.card.err{background:#fbdcdc;border-color:#e8a3a3;color:#7a1c1c}.card.err p{color:#8a2a2a}.badge.err{background:#b42318;color:#fff}
.info{color:#2e6fd8}
pre{margin:6px 0 0;padding:8px 10px;border-radius:6px;background:#fff6;font:12px/1.45 ui-monospace,Consolas,monospace;white-space:pre-wrap;word-break:break-all}
.why{margin-top:26px;border-top:1px solid #e4e7ec;padding-top:16px}.why h2{font-size:16px;margin:0 0 8px}
.why ol{margin:0;padding-left:20px}.why li{margin-bottom:4px}
.note{color:#667085;font-size:12px;margin-top:18px}
"""


def esc(s):
    return html.escape(str(s), quote=False)


def render(trace, cards, steps, findings, chain, t0, tz, request, pending_calls, obs_all):
    tzinfo = timezone(timedelta(hours=tz))

    def clock(t):
        return t.astimezone(tzinfo).strftime('%H:%M:%S') if t else ''

    by_gid = {}
    for x in findings:
        if x.get('gid'):
            by_gid.setdefault(x['gid'], []).append(x)
    rows = []
    gens = [s for s in steps if s['kind'] == 'gen']
    lat = (max(s['t'] for s in steps) - t0).total_seconds() if steps else 0
    ends = [parse_time(o.get('endTime')) for o in obs_all if o.get('endTime')]
    if ends:
        lat = max(lat, (max(ends) - t0).total_seconds())
    for c in cards:
        g, tools = c['gen'], c['tools']
        if g:
            fl = by_gid.get(g['id'], [])
            if fl:
                # thẻ cảnh báo của lượt sinh
                for x in fl:
                    rows.append((x['t'] or g['t'], x['level'], f'<h3>{esc(x["title"])}</h3><p>{esc(x["detail"])}</p>'))
            if not fl:
                rows.append((g['t'], 'info', f'<h3>Model suy nghĩ <span class="meta">{esc(fmt_dur(g["dur"]))} · vào {esc(fmt_tok(g["in"]))} · reasoning {esc(fmt_tok(g["reasoning"]))} · ra {g["out"]} token</span></h3>'))
        ok = [s for s in tools if s['kind'] == 'tool' and not s['error']]
        if ok:
            total = sum(s['n'] for s in ok)
            dur = (max(s['t'] + timedelta(seconds=s['dur'] or 0) for s in ok) - ok[0]['t']).total_seconds()
            names = ', '.join(f'{s["name"].replace("goconnect_", "")}' + (f' ×{s["n"]}' if s['n'] > 1 else '') for s in ok)
            bad_n = sum(len(s['error']) for s in tools if s['kind'] == 'tool')
            title = f'Gọi {total} tool' if total > 1 else f'Gọi tool {ok[0]["name"].replace("goconnect_", "")}'
            rows.append((ok[0]['t'], 'ok', f'<h3>{esc(title)} <span class="badge ok">{total}/{total + bad_n} OK</span> <span class="meta">{esc(fmt_dur(dur))}</span></h3>' + (f'<p>{esc(names)}</p>' if total > 1 else '')))
        for s in tools:
            if s['kind'] != 'tool' or not s['error']:
                continue
            e = s['error'][0]
            cmd = ''
            for tc in pending_calls:
                if tc.get('name') == s['name']:
                    try:
                        a = json.loads(tc.get('arguments') or '{}')
                        cmd = a.get('command') or json.dumps(a, ensure_ascii=False)
                    except ValueError:
                        cmd = str(tc.get('arguments'))
            body = f'<h3>{esc(s["name"])} <span class="badge err">{"TỪ CHỐI" if "permission" in (e.get("statusMessage") or "").lower() else "LỖI"}</span></h3><p>{esc(trunc(e.get("statusMessage"), 220))}</p>'
            if cmd:
                body += f'<pre>{esc(trunc(cmd, 420))}</pre>'
            rows.append((s['t'], 'err', body))
    # thẻ cảnh báo mức bước (không gắn lượt sinh) và kết luận
    for x in findings:
        if x['id'] == 'no_answer':
            rows.append(((x['t'] or t0) + timedelta(milliseconds=1), 'err', f'<h3>{esc(x["title"])}</h3><p>{esc(x["detail"])}</p>'))
        elif x['id'] == 'think_loop':
            rows.append((x['t'] or t0, 'err', f'<h3>{esc(x["title"])}</h3><p>{esc(x["detail"])}</p>'))
    # bỏ trùng thẻ cảnh báo cùng tiêu đề
    seen, rows2 = set(), []
    for t, lvl, body in sorted(rows, key=lambda r: r[0]):
        key = re.sub(r'<[^>]+>', '', body)[:90]
        if key in seen:
            continue
        seen.add(key)
        rows2.append((t, lvl, body))
    out = []
    for t, lvl, body in rows2:
        out.append(f'<div class="row"><div class="time">{clock(t)}</div><div class="rail"><div class="dot {lvl}"></div></div>'
                   f'<div class="card {lvl}">{body}</div></div>')
    n_err = sum(1 for x in findings if x['level'] == 'err')
    n_warn = sum(1 for x in findings if x['level'] == 'warn')
    ntools = sum(s['n'] for s in steps if s['kind'] == 'tool')
    peak = max((g['in'] for g in gens), default=0)
    meta = trace['_meta'] if isinstance(trace['_meta'], dict) else {}
    ra = meta.get('resourceAttributes') or {}
    who = ra.get('employeeName') or trace.get('userId') or ''
    stats = [(fmt_dur(lat), 'Tổng thời gian'), (str(len(gens)), 'Lượt gọi model'), (str(ntools), 'Lần gọi tool'),
             (fmt_tok(peak), 'Ngữ cảnh đỉnh'), (str(n_err), 'Lỗi'), (str(n_warn), 'Cảnh báo')]
    stats_html = ''.join(f'<div class="stat"><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in stats)
    why = ''
    if chain:
        why = '<div class="why"><h2>Vì sao lỗi</h2><ol>' + ''.join(f'<li>{esc(c)}</li>' for c in chain) + '</ol></div>'
    title = f'{trace.get("name") or "trace"} · {clock(t0)} {t0.astimezone(tzinfo):%d/%m/%Y}'
    return f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><title>{esc(title)}</title><style>{CSS}</style></head><body>
<div class="wrap"><h1>Dòng thời gian lượt chạy</h1>
<div class="sub">{esc(title)}{(' · ' + esc(who)) if who else ''} · trace {esc(trace.get('id', '')[:12])}</div>
{('<div class="req"><b>Yêu cầu:</b> ' + esc(request) + '</div>') if request else ''}
<div class="stats">{stats_html}</div>
<div class="tl">{''.join(out)}</div>
{why}
<div class="note">Dấu hiệu do luật tự động phát hiện từ số token, thời gian và trạng thái tool; nội dung tool không có trong log nên chỉ có tên và số lần gọi.</div>
</div>
<script>window.addEventListener('load',function(){{document.title='H='+document.documentElement.scrollHeight}})</script></body></html>"""


# ---- PNG qua trình duyệt ----------------------------------------------------------------------
def find_browser():
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'msedge', 'chrome'):
        p = shutil.which(name)
        if p:
            return p
    for p in (r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
              '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        if os.path.exists(p):
            return p
    return None


def to_png(html_path, png_path, width=1020):
    b = find_browser()
    if not b:
        return False, 'Không tìm thấy Chrome/Edge để xuất PNG'
    uri = Path(html_path).resolve().as_uri()
    prof = tempfile.mkdtemp(prefix='trace-viz-')
    base = [b, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars', f'--user-data-dir={prof}']
    try:
        r = subprocess.run(base + [f'--window-size={width},1000', '--virtual-time-budget=2000', '--dump-dom', uri],
                           capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace')
        m = re.search(r'<title>H=(\d+)</title>', r.stdout)
        h = int(m.group(1)) + 20 if m else 2400
        subprocess.run(base + [f'--window-size={width},{h}', f'--screenshot={png_path}', uri], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    return Path(png_path).exists(), ''


# ---- main -------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('--out', default='trace-viz-output')
    ap.add_argument('--tz', type=float, default=7, help='múi giờ hiển thị (mặc định UTC+7)')
    ap.add_argument('--no-png', action='store_true')
    a = ap.parse_args()

    trace, obs = read_trace(a.input)
    if not obs:
        raise SystemExit('Log không có observation nào để vẽ.')
    t0, steps = build_steps(trace, obs)
    content, pending, thinking = final_output(trace)
    request = user_request(trace)
    findings = detect(trace, obs, steps, thinking, content, pending)
    findings.sort(key=lambda x: (x['t'] is None, x['t']))
    chain = explain(findings)
    cards = merge_tool_batches(steps)
    doc = render(trace, cards, steps, findings, chain, t0, a.tz, request, pending, obs)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = 'trace-' + (trace.get('id') or 'log')[:8]
    hp, pp = out / f'{stem}.html', out / f'{stem}.png'
    hp.write_text(doc, encoding='utf-8')
    png_ok, png_err = (False, 'bỏ qua (--no-png)') if a.no_png else to_png(hp, pp)

    tzinfo = timezone(timedelta(hours=a.tz))
    span = (max(parse_time(o.get('endTime') or o['startTime']) for o in obs) - t0).total_seconds()
    print(f'TRACE {trace.get("id")} · {trace.get("name")} · {span:.1f}s · {len(obs)} observation')
    print(f'YÊU CẦU: {request}')
    print('\nCÁC BƯỚC:')
    for c in cards:
        g = c['gen']
        if g:
            print(f'  {g["t"].astimezone(tzinfo):%H:%M:%S} model  in={g["in"]} out={g["out"]} reasoning={g["reasoning"]} {fmt_dur(g["dur"])}')
        for s in c['tools']:
            st = 'LỖI' if s['error'] else 'OK'
            print(f'  {s["t"].astimezone(tzinfo):%H:%M:%S}   tool {s["name"]} ×{s["n"]} {st}')
    print('\nDẤU HIỆU:')
    for x in findings:
        print(f'  [{x["level"].upper()}] {x["title"]} — {x["detail"]}')
    if not findings:
        print('  (không phát hiện dấu hiệu bất thường theo các luật hiện có)')
    print('\nCHUỖI NGUYÊN NHÂN (suy từ luật, hãy kiểm lại rồi viết lại cho người đọc):')
    for i, c in enumerate(chain, 1):
        print(f'  {i}. {c}')
    print(f'\nHTML: {hp}')
    print(f'PNG: {pp}' if png_ok else f'PNG: không tạo được ({png_err})')


if __name__ == '__main__':
    sys.exit(main())
