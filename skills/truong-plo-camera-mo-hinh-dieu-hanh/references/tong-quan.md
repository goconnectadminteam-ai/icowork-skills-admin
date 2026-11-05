# Tổng quan mô hình điều hành GTM PLO Camera (theo 7 playbook 5 Rõ)

Nguồn: Playbook vận hành 5 Rõ — GTM PLO Camera, VNPT VinaPhone – Ban Sản phẩm – PLO Camera. Tài liệu tham chiếu gốc: "Bản Tổ chức triển khai, quản trị PLO Camera" (56 luồng nghiệp vụ, các Phần II–X). Ký hiệu [PBn Mục x].

## 1. Năm chữ "Rõ" = 7 mục của mỗi playbook

| Mục | Nội dung |
|---|---|
| 1. Làm gì | Mục tiêu được giao và chỉ số theo dõi |
| 2. Làm sao | Luồng nghiệp vụ phụ trách |
| 3. Công việc hằng ngày/tuần/tháng | Nhịp làm việc |
| 4. War room | Tần suất, agenda, tham dự ở đâu |
| 5. Điều hành | Quyền quyết định: tự quyết / đề xuất / escalate |
| 6. Người dự phòng & đầu mối | Hỏi ai khi vướng |
| 7. Nguyên tắc phối hợp | Cây chẩn đoán, giới hạn thẩm quyền |

## 2. Cây tổ chức điều hành Camera tại một tỉnh

```
War room cấp Toàn quốc  (PTGĐ VNPT VinaPhone chủ trì – PB7 Mục 4; xem khoảng trống K2)
        ▲ Loại 4, Loại 5 toàn quốc
Phó Giám đốc VNPT T/TP phụ trách BRCĐ  — accountable cuối cùng; Portfolio Review tháng; duyệt Loại 2, quyết Loại 3
        ▲ Loại 2 trở lên            │ ủy quyền
Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) — Loại 1; War room Tỉnh hằng tuần; chủ sở hữu CX toàn trình  [chưa có playbook]
        │ quản lý trực tiếp (giao việc, đánh giá, họp thường xuyên)
 ┌──────────────────────┬────────────────────────┬──────────────────────────┐
GĐ VNPT KV              GĐ TTVT KV                GĐ TT CSKH
 (WR KV hằng ngày)       (WR TTVT hằng ngày)       (WR TT CSKH hằng ngày)
   │                       │                          │
 NVKD                    NVKT                       Nhân viên OB (không dự war room)
```

## 3. Bốn trục mục tiêu và ai giữ trục nào

| Trục | Cấp Tỉnh | VNPT KV | TTVT KV | TT CSKH | Thực thi |
|---|---|---|---|---|---|
| Sản lượng PTM (MỚI) | Trưởng PLO cấp Tỉnh | Giám đốc | Attach kiêm nhiệm | Điểm chạm tổng đài | NVKD; NVKT (B2A) |
| Doanh thu | Trưởng PLO cấp Tỉnh | Giám đốc | Doanh thu Giữ tại nhà | Doanh thu Giữ online | NVKD; NV OB (thu cước) |
| Giữ khách (GIỮ) | Trưởng PLO cấp Tỉnh | Cảnh báo sớm | Cứu tại nhà | Cứu Bậc 3, GHTT | NVKT; NV OB |
| CX | Trưởng PLO cấp Tỉnh (chủ sở hữu toàn trình) | CSAT, đơn bị chặn | SLA lắp/sửa | Service Recovery | NVKD; NVKT |

## 4. Năm loại quyết định

| Loại | Nội dung | Ai quyết, cách quyết |
|---|---|---|
| 1 | Vận hành trong hạn mức | Trưởng PLO cấp Tỉnh tự quyết trong War room Tỉnh |
| 2 | Vượt hạn mức ủy quyền | PGĐ BRCĐ duyệt async 24–48 giờ qua hệ thống, không họp |
| 3 | Xung đột nguồn lực liên PLO/kênh trong tỉnh | PGĐ BRCĐ tại Portfolio Review cấp Tỉnh hoặc War room địa bàn |
| 4 | Sự cố nghiêm trọng (Luồng 8.1, khủng hoảng CX) | Họp khẩn ngay; ghi T0 ≤ 1 giờ; báo War room Toàn quốc |
| 5 | Thay đổi chính sách/mô hình | Thẩm quyền Lãnh đạo T/TP → Portfolio Review tỉnh; giá/sản phẩm toàn quốc → War room Toàn quốc |

## 5. Sáu cấp họp

| Cấp | Chủ trì | Nhịp | Agenda |
|---|---|---|---|
| War room Toàn quốc | PTGĐ VNPT VinaPhone | Tháng/quý; khi Loại 4 | — |
| Portfolio Review cấp Tỉnh | PGĐ BRCĐ | Tháng (~60' Camera / ~480' cho 8 PLO/kênh) | Toàn danh mục; Loại 3, 5 |
| War room cấp VNPT T/TP | Trưởng PLO cấp Tỉnh | Tuần | (chưa có trong 7 playbook) |
| War room VNPT KV | GĐ VNPT KV | Ngày | 10' mục tiêu – 30' đỏ/vàng – 15' quyết định – 5' giao việc qua App Employee |
| War room TTVT KV | GĐ TTVT KV | Ngày | cùng khung 10–30–15–5 |
| War room TT CSKH | GĐ TT CSKH | Ngày | cùng khung 10–30–15–5 |

## 6. Ba nguyên tắc xuyên suốt

- **B2A là quy trình, không phải vị trí:** NVKT và NVKD thực hiện tại mọi điểm chạm tự nhiên (lắp Fiber mới, sửa chữa, thu cước, GHTT); 4 bước; từ chối 3 lần → hệ thống dừng; kết quả không được sửa sau khi đã tính kỳ. [PB4 Mục 2.3]
- **Không ai tự đặt giá/ưu đãi ngoài chính sách.** [PB2, 3, 5, 8, 7]
- **Luồng 8.1 (bảo mật dữ liệu hình ảnh) luôn là Loại 4** — rủi ro cao nhất trong 56 luồng. [PB4 Mục 2.4; PB6 Mục 2]

## 7. Khoảng trống của bộ tài liệu

Chạy `python scripts/tra_cuu.py --khoang-trong`. Khi câu trả lời chạm tới một khoảng trống, phải nêu mã K tương ứng.
