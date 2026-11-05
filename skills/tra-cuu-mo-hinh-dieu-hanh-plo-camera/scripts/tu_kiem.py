#!/usr/bin/env python3
"""Tự kiểm dữ liệu: mỗi đáp án trong examples/cau-hoi-mau.md phải tra cứu ra được bằng tra_cuu.py."""
import subprocess
import sys
import os

GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CA = [
    (["--ai-quyet", "giá đặc biệt"], ["báo Giám đốc VNPT KV", "PB3 Mục 5"]),
    (["--loai", "2"], ["24–48", "không cần họp"]),
    (["--loai", "3"], ["Portfolio Review"]),
    (["--luong", "8.1"], ["T0", "Loại quyết định: 4"]),
    (["--war-room", "ttvt"], ["10'", "30'", "15'", "5'", "App Employee"]),
    (["--vi-tri", "ob"], ["không tham dự", "PB8"]),
    (["--tim", "KHÔNG phải một nhiệm vụ tách biệt"], ["PB4"]),
    (["--ai-quyet", "từ chối B2A"], ["tự dừng chu kỳ"]),
    (["--chan-doan", "giữ khách"], ["72 giờ", "TT CSKH"]),
    (["--vi-tri", "pho giam doc"], ["accountable"]),
    (["--khoang-trong"], ["K1", "K7"]),
    (["--vi-tri", "truong plo"], ["CHƯA CÓ PLAYBOOK", "Loại 1"]),
    (["--ai-quyet", "quét sai serial"], ["khóa cứng"]),
    (["--war-room", "portfolio"], ["480"]),
    (["--vi-tri", "Trưởng PLO cấp tỉnh"], ["PTM Tỉnh", "Doanh thu Tỉnh", "Giữ khách Tỉnh", "CX Tỉnh", "PB7 Mục 1", "K1"]),
]
loi = 0
for arg, can in CA:
    out = subprocess.run([sys.executable, os.path.join(GOC, "scripts", "tra_cuu.py")] + arg, capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"}).stdout
    thieu = [c for c in can if c not in out]
    print(("OK   " if not thieu else "LỖI ") + " ".join(arg) + (f"  — thiếu: {thieu}" if thieu else ""))
    loi += bool(thieu)
# File đọc sẵn phải khớp dữ liệu hiện tại (nhắc chạy sinh_tai_lieu.py sau khi sửa mo_hinh.json)
sys.path.insert(0, os.path.join(GOC, "scripts"))
import sinh_tai_lieu as S  # noqa: E402
for ten, ham in (("the-vi-tri.md", S.the_vi_tri), ("bang-tra.md", S.bang_tra)):
    p = os.path.join(GOC, "references", ten)
    khop = os.path.exists(p) and open(p, encoding="utf-8").read() == ham()
    print(("OK   " if khop else "LỖI ") + f"references/{ten} khớp data/mo_hinh.json" + ("" if khop else "  — chạy: python scripts/sinh_tai_lieu.py"))
    loi += not khop
print(f"\n{len(CA) + 2 - loi}/{len(CA) + 2} đạt")
sys.exit(1 if loi else 0)
