#!/usr/bin/env python3
"""Playbook xử lý vấn đề PLO Camera — tra cứu tài liệu GTM (bản chính thức 02/9/2026). Chỉ dùng thư viện chuẩn.

  python scripts/xu_ly.py --van-de "camera khách offline, xử lý chậm"   # nhận diện vấn đề → playbook
  python scripts/xu_ly.py --cay 1                 # cây chẩn đoán (1 Sản lượng, 2 Doanh thu, 3 Giữ khách, 4 CSAT)
  python scripts/xu_ly.py --luong 5.3             # SLA, escalation, trạng thái, file của một luồng
  python scripts/xu_ly.py --chi-so "PSSL"         # công thức, ngưỡng đèn, chủ sở hữu của chỉ tiêu
  python scripts/xu_ly.py --loai 2                # loại quyết định: ví dụ, cấp quyết, hình thức
  python scripts/xu_ly.py --nguyen-nhan "hoa hồng" # nhóm nguyên nhân → chủ sở hữu xử lý (X.B)
  python scripts/xu_ly.py --tim "điều chuyển ứng cứu"  # tìm toàn văn, có trang
  python scripts/xu_ly.py --muc X-G               # đường dẫn và đầu mục của một phần
  python scripts/xu_ly.py --can-xac-nhan          # điểm chưa chốt / mâu thuẫn
  python scripts/xu_ly.py --danh-muc              # danh mục 109 phần
"""
import argparse
import json
import math
import os
import re
import unicodedata
from collections import Counter

GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
def doc(p): return json.load(open(os.path.join(GOC, p), encoding="utf-8"))
IDX = {x["id"]: x for x in doc("data/chi_muc.json")}
TC, CAY, BCS, UQ, XN = doc("data/trieu_chung.json"), doc("data/cay_chan_doan.json"), doc("data/bo_chi_so.json"), doc("data/uy_quyen.json"), doc("data/can_xac_nhan.json")


def bd(s):
    s = unicodedata.normalize("NFD", (s or "").lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


TU_BO = set("va cua cho co khong la thi khi trong voi duoc bi nhung cac mot nay do de tu ve len o tai nhu hay da dang can phai theo".split())


def tok(s):
    return [w for w in re.findall(r"[a-z0-9]+", bd(s)) if w not in TU_BO and len(w) > 1]


def doc_muc(id_):
    return open(os.path.join(GOC, IDX[id_]["file"]), encoding="utf-8").read()


def ten(id_):
    x = IDX[id_]
    return f"{x['ten']} (trang PDF {x['trang'][0]}–{x['trang'][1]})"


def in_luong(id_, n_sla=4, n_esc=3):
    x = IDX[id_]
    print(f"- {ten(id_)}" + (f" — trạng thái: {x['trang_thai']}" if x.get("trang_thai") else ""))
    for s in x.get("sla", [])[:n_sla]:
        print(f"    · SLA: {s}")
    for e in x.get("escalation", [])[:n_esc]:
        print(f"    · Chuyển cấp: {e}")
    print(f"    · Đọc: {x['file']}")


def in_cay(n):
    c = CAY[n - 1]
    print(f"## Cây chẩn đoán {n} — Khi {c['khi']} [IX-C]\nTrình tự: {c['trinh_tu']}")
    for b in c["buoc"]:
        print(f"- {b['thu_tu']} │ Hỏi: {b['cau_hoi']} │ Nguyên nhân có thể: {b['nguyen_nhan']} │ Ai xử lý: {b['ai_xu_ly']} │ Làm gì: {b['hanh_dong']}")


def doan_loai(q):
    k = bd(q)
    if re.search(r"(?<![a-z])lo (?:len|ra|lot)|\bvideo\b", k) or any(w in k for w in ["lo lot", "ro ri", "hinh anh", "bao mat", "bao chi", "co quan quan ly", "truy cap trai phep"]):
        return "4"
    if any(w in k for w in ["xung dot", "dung chung", "mesh", "mytv", "vtci", "lien plo", "tu choi dieu chuyen"]):
        return "3"
    if any(w in k for w in ["bang gia", "doi gia", "cau truc goi", "co che nen", "tam ngung ban", "mo hinh dau moi"]):
        return "5"
    if any(w in k for w in ["vuot han muc", "ngan sach", "bo sung ngan sach", "ngoai le"]):
        return "2"
    return "1"


def bm25(q, k=4, bo=()):
    qt = tok(q)
    if not qt:
        return []
    docs = {i: tok(doc_muc(i)) for i in IDX}
    N, avg = len(docs), sum(len(v) for v in docs.values()) / len(docs)
    df = Counter(w for v in docs.values() for w in set(v))
    sc = []
    for i, v in docs.items():
        if i in bo:
            continue
        tf = Counter(v)
        s = sum(math.log(1 + (N - df[w] + .5) / (df[w] + .5)) * tf[w] * 2.2 / (tf[w] + 1.2 * (.25 + .75 * len(v) / avg)) for w in qt if w in tf)
        if s > 0:
            sc.append((s, i))
    return [i for _, i in sorted(sc, reverse=True)[:k]]


def van_de(q):
    k = bd(q)
    diem = []
    for t in TC:
        s = sum(2 if " " in bd(w) else 1 for w in t["tu_khoa"] if re.search(r"(?<![a-z0-9])" + re.escape(bd(w)) + r"(?![a-z0-9])", k))
        if t["ma"] == "l-baomat" and s:
            s += 3  # rủi ro cao nhất: luôn xét trước
        s += 0.3 * len(set(tok(q)) & set(tok(t["mo_ta"])))
        if s > 0:
            diem.append((s, t))
    diem.sort(key=lambda x: -x[0])
    chon = [t for s, t in diem[:3] if s >= max(1, diem[0][0] * 0.5)] if diem else []
    print(f"# Vấn đề: {q}")
    if not chon:
        print("Không khớp mẫu vấn đề nào trong bảng triệu chứng — dùng kết quả tìm toàn văn bên dưới và hỏi thêm người dùng.")
    da = set()
    for t in chon:
        print(f"\n## Nhận diện: {t['mo_ta']} (nhóm: {t['nhom']}, mã {t['ma']})")
        if t.get("cay"):
            in_cay(t["cay"])
        moi = [l for l in t["luong"] if l not in da]
        if moi:
            print("Luồng nghiệp vụ liên quan:")
            for l in moi:
                in_luong(l); da.add(l)
        elif t["luong"]:
            print("Luồng nghiệp vụ liên quan: " + ", ".join(t["luong"]) + " (đã liệt kê ở trên)")
        if t["muc"]:
            print("Phần tham chiếu: " + "; ".join(f"{m} = {ten(m)}" for m in t["muc"]))
            da |= set(t["muc"])
    them = bm25(q, 4, bo=da) if not chon else []
    if them:
        print("\n## Phần khác có thể liên quan (tìm toàn văn): " + "; ".join(f"{i} = {ten(i)}" for i in them))
    l = doan_loai(q)
    u = UQ["loai"][l]
    print(f"\n## Thẩm quyền gợi ý (cần đối chiếu): Loại {l} – {u['ten']} → {u['cap']}. {u['hinh_thuc']} [{u['nguon']}]")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--van-de"); g.add_argument("--cay", type=int, choices=[1, 2, 3, 4]); g.add_argument("--luong")
    g.add_argument("--chi-so"); g.add_argument("--loai", choices=list("12345")); g.add_argument("--nguyen-nhan")
    g.add_argument("--tim"); g.add_argument("--muc"); g.add_argument("--can-xac-nhan", action="store_true")
    g.add_argument("--danh-muc", action="store_true")
    a = ap.parse_args()

    if a.van_de:
        van_de(a.van_de)
    elif a.cay:
        in_cay(a.cay)
    elif a.luong:
        id_ = "L-" + a.luong.replace("L-", "")
        if id_ in IDX:
            in_luong(id_, 20, 10)
        else:
            print(f"Không có luồng {a.luong}. Chạy --danh-muc.")
    elif a.chi_so:
        k = set(tok(a.chi_so))
        kq = sorted(BCS, key=lambda d: -len(k & set(tok(d["chi_tieu"] + " " + d["cong_thuc"]))))[:4]
        for d in kq:
            if not k & set(tok(d["chi_tieu"] + " " + d["cong_thuc"])):
                break
            print(f"## {d['chi_tieu']} [IX-B, trang PDF {d['trang']}]\n- Công thức: {d['cong_thuc']}\n- Nguồn: {d['nguon_so_lieu']} │ Cấp: {d['cap_ap_dung']} │ Tần suất: {d['tan_suat']}\n- Ngưỡng: {d['nguong']}\n- Chủ sở hữu: toàn quốc {d['chu_so_huu_toan_quoc']} │ tỉnh {d['chu_so_huu_tinh']} │ khu vực {d['chu_so_huu_kv']} │ thực hiện {d['nguoi_thuc_hien']}")
    elif a.loai:
        u = UQ["loai"][a.loai]
        print(f"Loại {a.loai} – {u['ten']}\n- Ví dụ: {u['vi_du']}\n- Cấp thẩm quyền: {u['cap']}\n- Hình thức: {u['hinh_thuc']}\n- Nguồn: {u['nguon']}")
        if a.loai == "3":
            print("- Escalation theo nhóm quy trình: xem --tim 'Loại 3' hoặc references/gtm/X-H.md")
    elif a.nguyen_nhan:
        k = bd(a.nguyen_nhan)
        for n in UQ["nhom_nguyen_nhan"]:
            if any(bd(w) in k for w in n["tu_khoa"]) or k in bd(n["nhom"]):
                print(f"- {n['nhom']} → {n['chu_so_huu']} [X-B]")
        for e in UQ["escalation_4_nhom"]:
            if any(w in k for w in tok(e["nhom"] + " " + e["truoc"])):
                print(f"- Escalation {e['nhom']}: {e['truoc']} → Loại {e['loai']}: {e['cach']} [X-H]")
    elif a.tim:
        k = bd(a.tim)
        n = 0
        for i, x in IDX.items():
            t = doc_muc(i)
            for m in re.finditer(re.escape(k), bd(t)):
                tr = re.findall(r"<!-- trang (\d+) -->", t[:m.start()])
                print(f"[{i} – {x['ten']}, trang PDF {tr[-1] if tr else x['trang'][0]}] …{re.sub(chr(10), ' ', t[max(0, m.start()-120):m.end()+200])}…")
                n += 1
                break
            if n >= 12:
                break
        if not n:
            print(f"Không có «{a.tim}» trong tài liệu GTM.")
    elif a.muc:
        if a.muc not in IDX:
            print("Không có mã này. Chạy --danh-muc.")
        else:
            print(f"{ten(a.muc)}\nĐọc: {IDX[a.muc]['file']}\n")
            print("\n".join(doc_muc(a.muc).split("\n")[:25]))
    elif a.can_xac_nhan:
        for x in XN:
            print(f"- [{x['ma']}] {x['noi_dung']} (nguồn: {x['nguon']})")
    elif a.danh_muc:
        for i, x in IDX.items():
            print(f"{i}: {x['ten']} — trang {x['trang'][0]}–{x['trang'][1]}" + (f" — {x['trang_thai']}" if x.get("trang_thai") else ""))


if __name__ == "__main__":
    main()
