# Ví dụ trả lời mẫu (few-shot)

## Ví dụ đúng — "Camera của khách offline 3 ngày, NVKT chưa xuống"

```
PLAYBOOK XỬ LÝ – Camera khách offline, xử lý báo hỏng chậm
1. Nhận diện: sự cố trong Luồng 5.3 Xử lý báo hỏng/sự cố kỹ thuật; nếu lặp ở nhiều khách thì là chỉ số Giữ khách/CSAT. [L-5.3, trang PDF 185–194]
2. Kiểm theo thứ tự (cây 3 – Giữ khách giảm): SLA báo hỏng có chậm không, cảnh báo AI Churn có đúng không → Lãnh đạo TTVT KV phối hợp Giám đốc TT CSKH rà phiếu tồn quá SLA 72 giờ theo từng NVKT. [IX-C, trang 56]
3. Xử lý theo luồng: Bước 1 tiếp nhận – tiền xử lý ≤ 30 phút; Bước 5 hỗ trợ từ xa (kiểm OneHome online/offline, khởi động lại, đồng bộ Cloud); Bước 6 không xử lý được từ xa thì phân đoạn và xuất phiếu đúng đơn vị (TTVT; lỗi nền tảng OneHome/Cloud → VNPT IT/VNPT Media). Quá 30 phút chưa xác định phân đoạn → báo cấp quản lý trực tiếp. [L-5.3]
4. Thẩm quyền & chuyển cấp: Loại 1 — xử lý trong War room vận hành hằng tuần; nếu do thiếu thiết bị thay thế → nhánh Inventory (X-H). [X-A]
5. Theo dõi bằng chỉ số: "Số lượng thuê bao báo hỏng" (tháng; thực hiện: NVKT). Ô ngưỡng của chỉ tiêu này bị cắt khi trích — đối chiếu tài liệu gốc. [IX-B, trang PDF 52]
6. Lưu ý: Luồng 5.3 trạng thái "Hoàn thiện". SLA chi tiết theo nhóm khách (A/B/C) xem Phụ lục A QT-1263 dẫn trong luồng.
```

## Ví dụ sai

```
Anh cho NVKT xuống ngay trong hôm nay, nếu không được thì báo Giám đốc VNPT tỉnh xử lý.
Thông thường SLA sửa chữa là 24 giờ.
```

Vì sao sai: không có nguồn; "24 giờ" tự đặt (tài liệu ghi ≤30 phút tiền xử lý, 72 giờ cho phiếu tồn); bỏ qua bước hỗ trợ từ xa; chuyển cấp sai (đây là Loại 1, không cần Giám đốc tỉnh).

## Ví dụ đúng — "Video camera của khách bị lộ lên mạng"

```
PLAYBOOK XỬ LÝ – Lộ dữ liệu hình ảnh khách hàng
⚠ LOẠI 4 – HỌP KHẨN NGAY, không qua phê duyệt async, không chờ lịch. Ghi mốc T0 trong ≤ 1 giờ. [X-A; X-H; L-8.1]
1. Nhận diện: Luồng 8.1 Xử lý sự cố bảo mật dữ liệu hình ảnh (rủi ro cao nhất); nếu đã lên báo chí/mạng xã hội thêm Luồng 8.7, truyền thông nội bộ Luồng 8.10.
...
6. Lưu ý: Luồng 8.1 đang là "Dự thảo mới — chờ ban hành chính thức QT-ATBM-CAM-01" — cần xác nhận khi áp dụng.
```
