#!/usr/bin/env python3
"""Sinh lại references/the-vi-tri.md và references/bang-tra.md từ data/mo_hinh.json.

Chạy sau mỗi lần sửa data/mo_hinh.json:  python scripts/sinh_tai_lieu.py
Hai file này để mô hình ĐỌC thay cho việc chạy tra_cuu.py (khi môi trường không chạy được lệnh).
"""
import os
import subprocess
import sys

GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(GOC, "scripts"))
import tra_cuu as T  # noqa: E402

D, VT, WR = T.D, T.VT, T.WR
THU_TU = ["truong_plo_tinh", "pgd_brcd", "gd_vnpt_kv", "gd_ttvt_kv", "gd_tt_cskh", "nvkd", "nvkt", "nv_ob"]


def chay(*arg):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, os.path.join(GOC, "scripts", "tra_cuu.py"), *arg],
                          capture_output=True, text=True, encoding="utf-8", env=env).stdout.strip()


def the_vi_tri():
    out = ["# Thẻ 5 Rõ của 8 vị trí", "",
           "Sinh tự động từ data/mo_hinh.json (scripts/sinh_tai_lieu.py). Đọc file này cho câu hỏi về MỘT vị trí. Mỗi dòng đã kèm nguồn [PBn Mục x].", ""]
    for m in THU_TU:
        out += [chay("--vi-tri", m), ""]
    out += ["## Khoảng trống K1–K8", chay("--khoang-trong"), ""]
    return "\n".join(out)


def bang_tra():
    o = ["# Bảng tra xuyên vị trí — mô hình điều hành GTM PLO Camera", "",
         "Sinh tự động từ data/mo_hinh.json (scripts/sinh_tai_lieu.py). Đọc file này cho câu hỏi liên quan NHIỀU vị trí:",
         "ai quyết việc gì, loại quyết định, war room, chuỗi báo cáo/leo thang, chỉ số lệch thì kiểm gì, luồng do ai phụ trách, kiểm phiếu giao việc.",
         "Giữ nguyên nguồn [PBn Mục x] khi trích. Mục nào không có ở đây và trong the-vi-tri.md → mở playbook tương ứng.", "",
         "Mục lục: 1. Việc → ai quyết · 2. 5 loại quyết định · 3. War room · 4. Chuỗi leo thang · 5. Cây chẩn đoán · 6. Luồng nghiệp vụ · 7. Nguyên tắc chung · 8. Khoảng trống", ""]

    o += ["## 1. Việc → ai quyết (quyền hạn của cả 8 vị trí)", "", "| Vị trí | Việc | Quyền hạn | Loại | Nguồn |", "|---|---|---|---|---|"]
    for m in THU_TU:
        for q in VT[m].get("quyen", []):
            o.append(f"| {VT[m]['ten']} | {q['viec']} | {q['quyen_han']} | {q.get('loai') or '—'} | {q['nguon']} |")
    o.append("")

    o += ["## 2. 5 loại quyết định", ""]
    for n in sorted(D["loai_quyet_dinh"]):
        o += [f"### Loại {n}", chay("--loai", n), ""]

    o += ["## 3. War room / Portfolio Review", "", chay("--war-room"), ""]

    o += ["## 4. Chuỗi báo cáo / leo thang", ""]
    for m in THU_TU:
        o.append(f"- {chay('--leo-thang', m)}")
    o.append("")

    o += ["## 5. Cây chẩn đoán — chỉ số lệch thì kiểm gì, ai xử lý", "", "| Chỉ số | Kiểm gì | Ai xử lý | Việc cụ thể | Nguồn |", "|---|---|---|---|---|"]
    for c in D["cay_chan_doan"]:
        o.append(f"| {c['chi_so']} | {c['buoc']} | {c['ai']} | {c['viec']} | {c['nguon']} |")
    o += ["", "Lưu ý K8: cây chẩn đoán đầy đủ (Phần IX, Mục C) chưa có; bảng trên ghép từ các playbook.", ""]

    o += ["## 6. Luồng nghiệp vụ → vị trí phụ trách/thực thi", "", "| Luồng | Tên | Vị trí | Nguồn |", "|---|---|---|---|"]
    for l, ten in D["luong"].items():
        vt = [VT[m]["ten"] for m in THU_TU if l in VT[m].get("luong", [])]
        so = sorted({f"PB{VT[m]['so']} Mục 2" for m in THU_TU if l in VT[m].get("luong", [])})
        o.append(f"| {l} | {ten} | {'; '.join(vt) or 'chưa quy định trong 7 playbook'} | {'; '.join(so) or '—'} |")
    o += ["", "Luồng 8.1 luôn là Loại 4: escalation ngay, ghi T0 ≤ 1 giờ, không chờ lịch họp.", ""]

    o += ["## 7. Nguyên tắc chung (áp cho mọi vị trí)", ""] + [f"- {x}" for x in D["nguyen_tac_chung"]] + [""]
    o += ["## 8. Khoảng trống / mâu thuẫn K1–K8", "", chay("--khoang-trong"), ""]
    return "\n".join(o)


if __name__ == "__main__":
    for ten, noi_dung in (("the-vi-tri.md", the_vi_tri()), ("bang-tra.md", bang_tra())):
        p = os.path.join(GOC, "references", ten)
        open(p, "w", encoding="utf-8").write(noi_dung)
        print(f"Đã ghi {p} ({len(noi_dung)} ký tự)")
