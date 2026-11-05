#!/usr/bin/env python3
"""Tra cứu mô hình điều hành GTM PLO Camera từ data/mo_hinh.json và 7 playbook. Chỉ dùng thư viện chuẩn.

Mỗi kết quả kèm nguồn [PBn Mục x] để mô hình ngôn ngữ trích dẫn, không tự suy diễn.

  python scripts/tra_cuu.py --vi-tri nvkt            # thẻ 5 Rõ của một vị trí (mã hoặc từ khóa tên)
  python scripts/tra_cuu.py --luong 4.2              # luồng do ai phụ trách / thực thi
  python scripts/tra_cuu.py --loai 2                 # loại quyết định: ai quyết, cách quyết
  python scripts/tra_cuu.py --war-room               # tất cả cấp war room (hoặc --war-room tt_cskh)
  python scripts/tra_cuu.py --ai-quyet "giá đặc biệt" # việc này ai được quyết
  python scripts/tra_cuu.py --leo-thang nv_ob        # chuỗi báo cáo/leo thang lên trên
  python scripts/tra_cuu.py --chan-doan "giữ khách"  # bước cây chẩn đoán và ai xử lý
  python scripts/tra_cuu.py --tim "AI Churn"         # tìm toàn văn trong 7 playbook, kèm mục
  python scripts/tra_cuu.py --khoang-trong           # điểm thiếu / mâu thuẫn trong bộ playbook
  python scripts/tra_cuu.py --danh-sach              # danh sách mã vị trí
"""
import argparse
import json
import os
import re
import sys
import unicodedata

# Windows console (cp1252/cp1258) làm hỏng tiếng Việt khi in → ép UTF-8
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = json.load(open(os.path.join(GOC, "data", "mo_hinh.json"), encoding="utf-8"))
VT, WR = D["vi_tri"], D["war_room"]


def bo_dau(s):
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


TU_BO = {"khach", "hang", "cho", "va", "co", "khong", "cua", "the", "nao", "ai", "duoc", "khi", "trong", "voi", "la",
         "thi", "nay", "do", "mot", "cac", "nhung", "de", "tu", "quyet", "viec", "theo", "ve", "len", "phai"}


def tu_khoa(s):
    return {w for w in re.findall(r"[a-z0-9.]+", bo_dau(s)) if w not in TU_BO and len(w) > 1}


def tim_vi_tri(q):
    if q in VT:
        return q
    k = bo_dau(q)
    bi_danh = {"pgd": "pgd_brcd", "pho giam doc": "pgd_brcd", "vnpt kv": "gd_vnpt_kv", "vnpt khu vuc": "gd_vnpt_kv",
               "nvkd": "nvkd", "kinh doanh": "nvkd", "nvkt": "nvkt", "ky thuat": "nvkt", "cskh": "gd_tt_cskh",
               "ttvt": "gd_ttvt_kv", "vien thong": "gd_ttvt_kv", "ob": "nv_ob", "outbound": "nv_ob",
               "truong plo": "truong_plo_tinh", "plo tinh": "truong_plo_tinh"}
    for a, m in bi_danh.items():
        if a in k:
            return m
    for m, v in VT.items():
        if k in bo_dau(v["ten"]):
            return m
    return None


def nguon(v, muc):
    return v.get("nguon_muc", {}).get(muc, f"PB{v['so']} Mục {muc}")


def the_vi_tri(m):
    v = VT[m]
    out = [f"## {v['ten']} (PB{v['so']})" + ("  — CHƯA CÓ PLAYBOOK, thông tin ghép từ playbook khác" if v.get("chua_co_playbook") else "")]
    for k, nhan in (("bao_cao", "Báo cáo"), ("vai", "Vai trò")):
        if v.get(k):
            out.append(f"- {nhan}: {v[k]}")
    if v.get("quan_ly"):
        out.append("- Quản lý trực tiếp: " + ", ".join(VT[x]["ten"] for x in v["quan_ly"]))
    if v.get("muc_tieu"):
        out.append("- Mục tiêu (Rõ việc): " + "; ".join(v["muc_tieu"]) + f" [{nguon(v, '1')}]")
    if v.get("kpi"):
        out.append("- KPI chi tiết: " + "; ".join(v["kpi"]) + f" [PB{v['so']} Mục 1]")
    if v.get("luong"):
        out.append("- Luồng nghiệp vụ: " + ", ".join(f"{l} {D['luong'].get(l, '')}" for l in v["luong"]) + f" [PB{v['so']} Mục 2]")
    if v.get("nhip"):
        out.append("- Nhịp làm việc: " + " | ".join(f"{k}: {x}" for k, x in v["nhip"].items()) + f" [PB{v['so']} Mục 3]")
    w = v.get("war_room", {})
    out.append("- War room: chủ trì " + (", ".join(WR[x]["ten"] if x in WR else x for x in w.get("chu_tri", [])) or "không")
               + "; tham dự " + (", ".join(WR.get(x.split(" ")[0], {}).get("ten", x) + (" " + x.split(" ", 1)[1] if " " in x else "") for x in w.get("tham_du", [])) or "không")
               + ("; không tham dự " + ", ".join(w["khong_tham_du"]) if w.get("khong_tham_du") else "") + f" [{nguon(v, '4')}]")
    for q in v.get("quyen", []):
        loai = f" (Loại {q['loai']})" if q.get("loai") else ""
        out.append(f"- Quyền: {q['viec']} → {q['quyen_han']}{loai} [{q['nguon']}]")
    if v.get("leo_thang_den"):
        out.append(f"- Vượt thẩm quyền báo: {VT.get(v['leo_thang_den'], WR.get(v['leo_thang_den'], {})).get('ten', v['leo_thang_den'])}")
    if v.get("lien_quan"):
        out.append("- Các bên liên quan: " + "; ".join(v["lien_quan"]) + f" [PB{v['so']} Mục 6]")
    if v.get("file"):
        out.append(f"- Toàn văn: {v['file']}")
    if v.get("chua_co_playbook"):
        out.append("- Khoảng trống: " + D["khoang_trong"]["K1"])
        out.append("- Khoảng trống: " + D["khoang_trong"]["K7"])
    return "\n".join(out)


def tim_toan_van(q):
    k = bo_dau(q)
    kq = []
    for m, v in VT.items():
        if not v.get("file"):
            continue
        muc = "đầu tài liệu"
        for dong in open(os.path.join(GOC, v["file"]), encoding="utf-8"):
            h = re.match(r"^#+\s*(.+)", dong)
            if h:
                muc = h.group(1).strip()
            if k in bo_dau(dong):
                kq.append(f"[PB{v['so']} {v['ten']} — {muc}] {dong.strip()[:300]}")
    return kq


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--vi-tri"); g.add_argument("--luong"); g.add_argument("--loai")
    g.add_argument("--war-room", nargs="?", const="*"); g.add_argument("--ai-quyet"); g.add_argument("--leo-thang")
    g.add_argument("--chan-doan"); g.add_argument("--tim"); g.add_argument("--khoang-trong", action="store_true")
    g.add_argument("--danh-sach", action="store_true")
    a = ap.parse_args()

    if a.danh_sach:
        for m, v in VT.items():
            print(f"{m}: {v['ten']} (PB{v['so']}){' – chưa có playbook' if v.get('chua_co_playbook') else ''}")
    elif a.vi_tri:
        m = tim_vi_tri(a.vi_tri)
        print(the_vi_tri(m) if m else f"Không tìm thấy vị trí «{a.vi_tri}». Chạy --danh-sach để xem mã.")
    elif a.luong:
        ten = D["luong"].get(a.luong)
        if not ten:
            print(f"Luồng {a.luong} không có trong 7 playbook.")
            return
        print(f"Luồng {a.luong}: {ten}")
        for m, v in VT.items():
            if a.luong in v.get("luong", []):
                print(f"- {v['ten']} [PB{v['so']} Mục 2]")
        if a.luong == "8.1":
            print(f"- Loại quyết định: 4 — {D['loai_quyet_dinh']['4']['ai_quyet']} [{D['loai_quyet_dinh']['4']['nguon']}]")
    elif a.loai:
        l = D["loai_quyet_dinh"].get(a.loai)
        print(f"Loại {a.loai} – {l['ten']}: {l['ai_quyet']} [{l['nguon']}]" if l else "Chỉ có Loại 1–5.")
        for m, v in VT.items():
            for q in v.get("quyen", []):
                if str(q.get("loai")) == a.loai:
                    print(f"- {v['ten']}: {q['viec']} → {q['quyen_han']} [{q['nguon']}]")
    elif a.war_room:
        for m, w in WR.items():
            if a.war_room != "*" and bo_dau(a.war_room) not in bo_dau(m + " " + w["ten"]):
                continue
            print(f"## {w['ten']} — chủ trì: {w['chu_tri']} — {w['tan_suat']} [{w['nguon']}]")
            for k in ("thanh_phan", "pham_vi", "du_lieu", "ghi_chu"):
                if w.get(k):
                    print(f"- {k.replace('_', ' ')}: {w[k]}")
            for x in w.get("agenda", []):
                print(f"- {x}")
    elif a.ai_quyet:
        k = tu_khoa(a.ai_quyet)
        diem = []
        for m, v in VT.items():
            for q in v.get("quyen", []):
                s = len(k & tu_khoa(q["viec"] + " " + q["quyen_han"]))
                if s:
                    diem.append((s, f"- {v['ten']}: {q['viec']} → {q['quyen_han']}" + (f" (Loại {q['loai']})" if q.get("loai") else "") + f" [{q['nguon']}]"))
        for _, x in sorted(diem, key=lambda t: -t[0])[:8]:
            print(x)
        if not diem:
            print("Không có dòng quyền hạn nào khớp trong 7 playbook. Thử --tim hoặc --loai.")
    elif a.leo_thang:
        m = tim_vi_tri(a.leo_thang)
        chuoi, da = [], set()
        while m and m not in da:
            da.add(m)
            ten = VT[m]["ten"] if m in VT else WR[m]["ten"]
            chuoi.append(ten + (" (chưa có playbook)" if VT.get(m, {}).get("chua_co_playbook") else ""))
            m = VT.get(m, {}).get("leo_thang_den")
        print(" → ".join(chuoi) if chuoi else "Không tìm thấy vị trí.")
    elif a.chan_doan:
        k = bo_dau(a.chan_doan)
        for c in D["cay_chan_doan"]:
            if k in bo_dau(c["chi_so"] + " " + c["buoc"]):
                print(f"- {c['chi_so']} │ {c['buoc']} │ ai xử lý: {c['ai']} │ việc: {c['viec']} [{c['nguon']}]")
    elif a.tim:
        kq = tim_toan_van(a.tim)
        print("\n".join(kq[:15]) if kq else f"Không có «{a.tim}» trong 7 playbook.")
    elif a.khoang_trong:
        for k, v in D["khoang_trong"].items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
