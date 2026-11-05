---
name: truong-plo-camera-xu-ly-van-de
description: Playbook xử lý vấn đề cho PLO Camera, tra theo tài liệu chính thức "Tổ chức triển khai, quản trị GTM PLO Camera" (02/9/2026) — khi chỉ số lệch (sản lượng PTM, doanh thu, giữ khách, CSAT, PSSL, B2A…) thì kiểm theo cây chẩn đoán nào, ai xử lý; khi có sự cố trong 56 luồng nghiệp vụ (thiếu thiết bị, báo hỏng, lộ hình ảnh, khiếu nại, hoàn tiền, nợ cước, hoa hồng, firmware, hợp đồng, OB…) thì luồng nào, bước nào, SLA bao nhiêu, chuyển cấp ra sao; khi cần biết thẩm quyền (Loại 1–5), phê duyệt bất đồng bộ, xung đột nguồn lực, họp nào. Dùng mỗi khi người dùng mô tả một vấn đề, sự cố, chỉ số đỏ/vàng, hoặc hỏi "xử lý thế nào", "ai quyết", "báo ai", "SLA bao nhiêu", "luồng nào" về Camera — kể cả khi không nhắc tên tài liệu.
---

# Playbook xử lý vấn đề PLO Camera

Nguồn duy nhất: tài liệu GTM PLO Camera, đã tách thành 109 phần trong `references/gtm/` (mỗi luồng một file) và dữ liệu có cấu trúc trong `data/`.
Không trả lời theo hiểu biết chung. Không đoán số, SLA, người xử lý. Mọi khẳng định kèm nguồn `[mã phần, trang PDF]`.

## 1. Quy trình

1. Chạy `python scripts/xu_ly.py --van-de "<mô tả vấn đề của người dùng>"`.
   Kết quả cho: loại vấn đề, cây chẩn đoán (nếu là chỉ số lệch), các luồng liên quan kèm SLA và chuyển cấp, phần tham chiếu, loại quyết định gợi ý.
2. Mở đúng 1–2 file được chỉ ra (`references/gtm/L-x.y.md` hoặc `X-A.md`…) để lấy bước xử lý cụ thể. Không mở cả bộ.
3. Cần thêm thì dùng: `--cay <1-4>`, `--luong <x.y>`, `--chi-so "<tên>"`, `--loai <1-5>`, `--nguyen-nhan "<nhóm>"`, `--tim "<từ khóa>"`, `--can-xac-nhan`.
4. Nếu `--van-de` không nhận diện được: hỏi người dùng đúng MỘT câu làm rõ (chỉ số nào, luồng nào, cấp nào) rồi dừng.

## 2. Mẫu trả lời — PLAYBOOK XỬ LÝ

```
PLAYBOOK XỬ LÝ – [tên vấn đề]
1. Nhận diện: [chỉ số lệch / sự cố luồng x.y / câu hỏi thẩm quyền] [nguồn]
2. Kiểm theo thứ tự: [các bước cây chẩn đoán: hỏi gì – nguyên nhân có thể – ai xử lý] [IX-C]
3. Xử lý theo luồng: [bước – actor – SLA – điểm chốt đối soát] [L-x.y, trang]
4. Thẩm quyền & chuyển cấp: [Loại n – ai quyết – hình thức (họp tuần / async 24–48h / Portfolio Review / họp khẩn)] [X-A, X-H, XI-C]
5. Theo dõi bằng chỉ số: [chỉ tiêu – ngưỡng đèn – chủ sở hữu] [IX-B]
6. Lưu ý: [trạng thái luồng nếu chưa "Hoàn thiện"; điểm chưa chốt/mâu thuẫn mã GTM-… hoặc LECH-…]
```
Mục nào tài liệu không có thì ghi "Tài liệu GTM chưa quy định", không bỏ trống im lặng, không tự điền.

## 3. Luật cứng

- **Lộ lọt dữ liệu hình ảnh, vụ việc lên báo chí/mạng xã hội, yêu cầu của cơ quan quản lý → luôn Loại 4**: họp khẩn ngay, không qua async, không chờ lịch; Luồng 8.1 ghi T0 ≤ 1 giờ. Nêu điều này ở dòng đầu câu trả lời. Lưu ý Luồng 8.1 đang là dự thảo chờ ban hành.
- Luồng có trạng thái khác "Hoàn thiện" (dự thảo, đang vận hành – bổ sung…) phải nói rõ trong mục Lưu ý.
- Hạn mức Loại 1/2 (đề xuất 50 triệu đồng), SLA phê duyệt async (24h/4h), ngưỡng đèn: đều là **đề xuất – cần xác nhận chính thức** theo tài liệu (IX-E, X-J). Không trình bày như đã chốt.
- Khi tài liệu GTM và Playbook 5 Rõ nói khác nhau (`--can-xac-nhan`, mã LECH-…), nêu cả hai và gắn nhãn cần xác nhận; không tự chọn một bên.
- Dùng chức danh, không dùng tên người. Danh sách đầu mối 34 tỉnh (họ tên, số điện thoại) đã được lược khỏi skill; nếu người dùng cần, chỉ tới tài liệu gốc trang 76–79.
- Không sửa số trong tài liệu (≤30 phút, 72 giờ, 24h/48h, 7 ngày, 85%…). Chép đúng.

## 4. Dùng cùng các skill khác

- `truong-plo-camera-mo-hinh-dieu-hanh`: Playbook 5 Rõ theo vị trí (ai làm gì hằng ngày). Skill này là tầng tài liệu gốc phía trên.
- `truong-plo-camera-chan-doan-lech`: tính số; skill này cho cây chẩn đoán chính thức và đầu mối để đối chiếu.
- `truong-plo-camera-ket-luan-phien`, `-ke-hoach-hanh-dong`: lấy mục 4 (thẩm quyền & chuyển cấp) để điền phần chuyển cấp.
