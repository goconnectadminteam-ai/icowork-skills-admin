#!/usr/bin/env python3
"""Tự kiểm: mỗi tình huống mẫu phải ra đúng luồng/phần và đúng loại quyết định."""
import os, subprocess, sys
GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CA = [
 ("--van-de", "camera của khách offline, NVKT xử lý chậm quá 72 giờ", ["Luồng 5.3", "Loại 1", "72 giờ"]),
 ("--van-de", "video camera của khách bị lộ lên mạng xã hội", ["Luồng 8.1", "Loại 4", "T0 ≤ 1 giờ"]),
 ("--van-de", "tỉnh hết thiết bị, đơn thoái trả do thiếu hàng hơn 7 ngày", ["Luồng 3.5", "Luồng 3.1"]),
 ("--van-de", "sản lượng PTM tháng này không đạt kế hoạch", ["Cây chẩn đoán 1", "Kiểm tra Inventory", "Kiểm tra cơ chế"]),
 ("--van-de", "doanh thu Camera lệch kế hoạch, nghi giao dịch treo", ["Cây chẩn đoán 2", "3 chiều"]),
 ("--van-de", "CSAT giảm, khách phàn nàn bị làm phiền nhiều lần", ["Cây chẩn đoán 4", "Customer Timeline"]),
 ("--van-de", "NVKT vừa bán Mesh vừa bán Camera, tỉnh muốn ưu tiên Mesh", ["Loại 3", "WR địa bàn"]),
 ("--van-de", "khách đòi giảm giá ngoài chính sách khi mua combo", ["Luồng 2.6"]),
 ("--van-de", "khách khiếu nại chính thức về cước", ["Luồng 5.9"]),
 ("--van-de", "cần bổ sung ngân sách khuyến mại giữa kỳ vượt hạn mức", ["Loại 2"]),
 ("--van-de", "nhiều nhân viên chưa được giao BSC Camera", ["Luồng 8.3"]),
 ("--van-de", "khách chuyển nhà muốn chuyển camera", ["Luồng 4.5"]),
 ("--luong", "8.1", ["Dự thảo", "T0"]),
 ("--loai", "2", ["24h/48h", "50 triệu"]),
 ("--chi-so", "tỷ lệ hoàn thành kế hoạch PTM", ["Ngưỡng", "80%"]),
 ("--nguyen-nhan", "hoa hồng thi đua", ["Ban Điều hành kinh doanh"]),
 ("--can-xac-nhan", None, ["LECH-1", "GTM-X.J-1"]),
]
loi = 0
for flag, q, can in CA:
    cmd = [sys.executable, os.path.join(GOC, "scripts", "xu_ly.py"), flag] + ([q] if q else [])
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    thieu = [c for c in can if c not in out]
    print(("OK   " if not thieu else "LỖI ") + f"{flag} {q or ''}" + (f" — thiếu {thieu}" if thieu else ""))
    loi += bool(thieu)
print(f"\n{len(CA)-loi}/{len(CA)} đạt"); sys.exit(1 if loi else 0)
