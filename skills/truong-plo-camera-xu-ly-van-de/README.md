# Cài và chạy thử — truong-plo-camera-xu-ly-van-de (v1, 03/11/2026)

Playbook xử lý vấn đề PLO Camera theo tài liệu "Tổ chức triển khai, quản trị GTM PLO Camera" (bản chính thức 02/9/2026, 312 trang).

## Cài vào opencode
Chép cả thư mục vào `.opencode/skills/truong-plo-camera-xu-ly-van-de/`. Chỉ cần Python 3 chuẩn.

## Kiểm (không cần mô hình)
```
python scripts/tu_kiem.py                       # 17/17 tình huống đạt
python scripts/xu_ly.py --van-de "camera khách offline, xử lý chậm"
python scripts/xu_ly.py --danh-muc              # 109 phần
python scripts/xu_ly.py --can-xac-nhan          # điểm chưa chốt và mâu thuẫn
```

## Cấu trúc
- `references/gtm/` — 109 phần: Phần I, IX (A theo 16 thẻ vai trò, B–E), X (A–J), XI (A–D), Mục 1–3, 56 luồng (mỗi luồng một file), XII, XIII, phụ lục đào tạo, thống kê công cụ.
- `data/chi_muc.json` — mục lục: trang PDF, trạng thái luồng, SLA và chuyển cấp trích tự động.
- `data/trieu_chung.json` — 56 mẫu vấn đề → cây chẩn đoán, luồng, phần tham chiếu.
- `data/cay_chan_doan.json` — 4 cây chẩn đoán (IX.C).
- `data/bo_chi_so.json` — 78 chỉ tiêu (IX.B): công thức, nguồn, tần suất, ngưỡng, chủ sở hữu.
- `data/uy_quyen.json` — 2 tầng điều hành, 5 loại quyết định, nhóm nguyên nhân, escalation 4 nhóm.
- `data/can_xac_nhan.json` — 9 điểm tài liệu tự ghi "cần xác nhận" + 4 điểm lệch với Playbook 5 Rõ.

## Giới hạn
- Văn bản được trích tự động từ PDF; bảng nhiều cột có chỗ bị ngắt dòng. Bộ chỉ số: một số ô ngưỡng bị cắt ở chỗ ngắt trang (ghi "🟢 Xanh" trống) — đối chiếu tài liệu gốc.
- Bảng họ tên, số điện thoại đầu mối 34 tỉnh (trang 76–79) được lược bỏ để bảo vệ thông tin cá nhân.
- Ánh xạ "vấn đề → luồng" là bảng đề xuất của người dựng skill; cần Trưởng PLO Camera rà lại.
