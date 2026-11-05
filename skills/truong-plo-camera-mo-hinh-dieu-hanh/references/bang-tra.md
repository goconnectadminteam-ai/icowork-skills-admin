# Bảng tra xuyên vị trí — mô hình điều hành GTM PLO Camera

Sinh tự động từ data/mo_hinh.json (scripts/sinh_tai_lieu.py). Đọc file này cho câu hỏi liên quan NHIỀU vị trí:
ai quyết việc gì, loại quyết định, war room, chuỗi báo cáo/leo thang, chỉ số lệch thì kiểm gì, luồng do ai phụ trách, kiểm phiếu giao việc.
Giữ nguyên nguồn [PBn Mục x] khi trích. Mục nào không có ở đây và trong the-vi-tri.md → mở playbook tương ứng.

Mục lục: 1. Việc → ai quyết · 2. 5 loại quyết định · 3. War room · 4. Chuỗi leo thang · 5. Cây chẩn đoán · 6. Luồng nghiệp vụ · 7. Nguyên tắc chung · 8. Khoảng trống

## 1. Việc → ai quyết (quyền hạn của cả 8 vị trí)

| Vị trí | Việc | Quyền hạn | Loại | Nguồn |
|---|---|---|---|---|
| Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) | Vận hành Camera trong War room Tỉnh, trong hạn mức được ủy quyền | Tự quyết | 1 | PB7 Mục 7 |
| Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) | Đề xuất vượt hạn mức ủy quyền | Escalate PGĐ BRCĐ phê duyệt async 24–48h | 2 | PB7 Mục 2, 5 |
| Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ | Chọn nhân sự đảm nhiệm Trưởng PLO cấp Tỉnh và phạm vi ủy quyền | Tự quyết trong nội bộ VNPT T/TP | — | PB7 Mục 5 |
| Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ | Đề xuất vượt hạn mức do Trưởng PLO cấp Tỉnh escalate | Phê duyệt bất đồng bộ 24–48 giờ qua hệ thống, không cần họp | 2 | PB7 Mục 5 |
| Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ | Xung đột nguồn lực giữa các PLO/kênh trong phạm vi 1 tỉnh | Quyết định tại Portfolio Review cấp Tỉnh hoặc War room địa bàn | 3 | PB7 Mục 5 |
| Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ | Chính sách giá/sản phẩm Camera toàn quốc | Không tự quyết — escalate War room Toàn quốc | 5 | PB7 Mục 5 |
| Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ | Sự cố nghiêm trọng (bảo mật dữ liệu hình ảnh – Luồng 8.1, khủng hoảng CX) | Họp khẩn ngay cùng Trưởng PLO cấp Tỉnh, không chờ lịch | 4 | PB7 Mục 5 |
| Giám đốc VNPT khu vực | Vận hành hằng ngày trong địa bàn (phân công NVKD, tổ chức bán hàng, điều chỉnh lịch hẹn) | Tự quyết ngay, không cần báo cáo trước | — | PB2 Mục 5 |
| Giám đốc VNPT khu vực | Thiếu tồn kho/nguồn lực vượt khả năng xử lý tại chỗ | Đề xuất bổ sung lên Trưởng PLO cấp Tỉnh | — | PB2 Mục 5 |
| Giám đốc VNPT khu vực | Sự cố kỹ thuật/CX nghiêm trọng tại địa bàn | Escalation ngay lên Trưởng PLO cấp Tỉnh, không chờ sinh hoạt đầu ca | — | PB2 Mục 5 |
| Giám đốc VNPT khu vực | Chính sách sản phẩm/marketing toàn quốc, giá/gói cước | Không tự xây dựng/quyết định — áp dụng chính sách đã ban hành | — | PB2 Mục 5 |
| Giám đốc TTVT khu vực | Phân công/điều chuyển NVKT trong địa bàn | Tự quyết ngay, không cần báo cáo trước | — | PB6 Mục 5 |
| Giám đốc TTVT khu vực | Thiếu thiết bị/nhân sự kéo dài ảnh hưởng SLA | Đề xuất bổ sung lên Trưởng PLO cấp Tỉnh | — | PB6 Mục 5 |
| Giám đốc TTVT khu vực | Sự cố kỹ thuật nghiêm trọng (an toàn lắp đặt, hư hỏng diện rộng, bảo mật dữ liệu hình ảnh – Luồng 8.1) | Escalation ngay lên Trưởng PLO cấp Tỉnh — họp khẩn | 4 | PB6 Mục 5 |
| Giám đốc Trung tâm CSKH (TT CSKH) | Gọi chăm sóc/gia hạn theo kịch bản chuẩn (kể cả đội OB) | Tự thực hiện, không xin phép từng cuộc gọi | — | PB5 Mục 5 |
| Giám đốc Trung tâm CSKH (TT CSKH) | Khách từ chối 3 lần liên tiếp | Tự động dừng chu kỳ tiếp cận | — | PB5 Mục 5 |
| Giám đốc Trung tâm CSKH (TT CSKH) | Phương án khiếu nại, bồi thường/hoàn tiền trong thẩm quyền phân cấp | Toàn quyền điều hành đội Tổng đài/CSKH | — | PB5 Mục 5 |
| Giám đốc Trung tâm CSKH (TT CSKH) | Khách vẫn không hài lòng sau Service Recovery; khiếu nại vượt thẩm quyền; báo hỏng/rời mạng lệch ngưỡng không tự xử lý được với TTVT | Escalation lên Trưởng PLO cấp Tỉnh | — | PB5 Mục 5 |
| Nhân viên kinh doanh (NVKD) | Áp dụng chính sách giá/khuyến mãi đã công bố | Tự thực hiện đúng bảng giá — không tự thay đổi | — | PB3 Mục 5 |
| Nhân viên kinh doanh (NVKD) | Khách yêu cầu ngoài chính sách chuẩn (giá đặc biệt, điều kiện riêng) | Không tự quyết — báo Giám đốc VNPT KV | — | PB3 Mục 5 |
| Nhân viên kinh doanh (NVKD) | Khách có dấu hiệu khiếu nại/rời mạng | Phối hợp B2A ngay; báo Giám đốc VNPT KV nếu cần hỗ trợ | — | PB3 Mục 5 |
| Nhân viên kinh doanh (NVKD) | Thứ tự ưu tiên phiếu/khách tiềm năng trong ca | Tự quyết trong ca theo hướng dẫn của Giám đốc VNPT KV | — | PB3 Mục 5 |
| Nhân viên kỹ thuật (NVKT) | Thứ tự xử lý phiếu trong ca | Tự sắp theo hẹn/SLA, theo hướng dẫn Giám đốc TTVT KV | — | PB4 Mục 5 |
| Nhân viên kỹ thuật (NVKT) | Phương án kỹ thuật tại hiện trường | Tự quyết trong quy chuẩn kỹ thuật | — | PB4 Mục 5 |
| Nhân viên kỹ thuật (NVKT) | Tiếp xúc B2A khi đến nhà khách | Tự thực hiện theo quy trình chuẩn, không cần xin phép | — | PB4 Mục 5 |
| Nhân viên kỹ thuật (NVKT) | Khách đã từ chối B2A đủ số lần quy định (3 lần liên tiếp) | Không tiếp cận thêm — hệ thống tự dừng chu kỳ | — | PB4 Mục 2.3, 5 |
| Nhân viên kỹ thuật (NVKT) | Quét sai serial | Được sửa trong thời hạn quy định trước khi khóa cứng; phát hiện muộn thì báo cáo | — | PB4 Mục 5 |
| Nhân viên kỹ thuật (NVKT) | Thiếu thiết bị/linh kiện, sự cố kỹ thuật phức tạp | Báo ngay Giám đốc TTVT KV — không tự trì hoãn mà không báo khách | — | PB4 Mục 5 |
| Nhân viên kỹ thuật (NVKT) | Sự cố an toàn bảo mật dữ liệu hình ảnh (Luồng 8.1) | Escalation ngay, ghi mốc T0 trong ≤ 1 giờ — không tự xử lý | 4 | PB4 Mục 2.4, 5 |
| Nhân viên kỹ thuật (NVKT) | App Employee/Inventory lỗi không đồng bộ | Báo ngay; không tự đóng phiếu Hoàn công khi chưa đồng bộ | — | PB4 Mục 6 |
| Nhân viên OB (TT CSKH) | Thời điểm và số lần gọi lại trong ngày theo quy trình | Tự quyết — không tự đặt ưu đãi ngoài chính sách | — | PB8 Mục 5 |
| Nhân viên OB (TT CSKH) | Khách đã từ chối đủ số lần / không liên hệ được | Không gọi thêm ngoài chu kỳ quy định | — | PB8 Mục 5 |
| Nhân viên OB (TT CSKH) | Khiếu nại hoặc yêu cầu vượt phạm vi outbound | Chuyển ngay Lãnh đạo TT CSKH — không tự xử lý | — | PB8 Mục 5 |

## 2. 5 loại quyết định

### Loại 1
Loại 1 – Vận hành trong hạn mức: Trưởng PLO cấp Tỉnh tự quyết trong War room Tỉnh [PB7 Mục 7]
- Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh): Vận hành Camera trong War room Tỉnh, trong hạn mức được ủy quyền → Tự quyết [PB7 Mục 7]

### Loại 2
Loại 2 – Vượt hạn mức ủy quyền: PGĐ VNPT T/TP phụ trách BRCĐ phê duyệt bất đồng bộ 24–48 giờ qua hệ thống, không cần họp [PB7 Mục 2, 5]
- Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ: Đề xuất vượt hạn mức do Trưởng PLO cấp Tỉnh escalate → Phê duyệt bất đồng bộ 24–48 giờ qua hệ thống, không cần họp [PB7 Mục 5]
- Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh): Đề xuất vượt hạn mức ủy quyền → Escalate PGĐ BRCĐ phê duyệt async 24–48h [PB7 Mục 2, 5]

### Loại 3
Loại 3 – Xung đột nguồn lực liên PLO/kênh trong phạm vi tỉnh: PGĐ BRCĐ tại Portfolio Review cấp Tỉnh hoặc War room địa bàn [PB7 Mục 2, 5]
- Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ: Xung đột nguồn lực giữa các PLO/kênh trong phạm vi 1 tỉnh → Quyết định tại Portfolio Review cấp Tỉnh hoặc War room địa bàn [PB7 Mục 5]

### Loại 4
Loại 4 – Sự cố nghiêm trọng (bảo mật dữ liệu hình ảnh – Luồng 8.1; khủng hoảng CX): Họp khẩn ngay (PGĐ BRCĐ cùng Trưởng PLO cấp Tỉnh); báo War room Toàn quốc; ghi mốc T0 ≤ 1 giờ [PB7 Mục 5; PB4 Mục 2.4; PB6 Mục 2]
- Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ: Sự cố nghiêm trọng (bảo mật dữ liệu hình ảnh – Luồng 8.1, khủng hoảng CX) → Họp khẩn ngay cùng Trưởng PLO cấp Tỉnh, không chờ lịch [PB7 Mục 5]
- Nhân viên kỹ thuật (NVKT): Sự cố an toàn bảo mật dữ liệu hình ảnh (Luồng 8.1) → Escalation ngay, ghi mốc T0 trong ≤ 1 giờ — không tự xử lý [PB4 Mục 2.4, 5]
- Giám đốc TTVT khu vực: Sự cố kỹ thuật nghiêm trọng (an toàn lắp đặt, hư hỏng diện rộng, bảo mật dữ liệu hình ảnh – Luồng 8.1) → Escalation ngay lên Trưởng PLO cấp Tỉnh — họp khẩn [PB6 Mục 5]

### Loại 5
Loại 5 – Thay đổi chính sách/mô hình: Thuộc thẩm quyền Lãnh đạo VNPT T/TP → Portfolio Review cấp Tỉnh; chính sách giá/sản phẩm Camera toàn quốc → War room Toàn quốc [PB7 Mục 2, 5]
- Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ: Chính sách giá/sản phẩm Camera toàn quốc → Không tự quyết — escalate War room Toàn quốc [PB7 Mục 5]

## 3. War room / Portfolio Review

## War room cấp Toàn quốc — chủ trì: PTGĐ VNPT VinaPhone (theo PB7 Mục 4) — Theo lịch tháng/quý; khi có Loại 4 [PB7 Mục 4]
- ghi chu: Xem khoang_trong K2 về người chủ trì.
## Portfolio Review cấp Tỉnh — chủ trì: PGĐ VNPT T/TP phụ trách BRCĐ — Hằng tháng; ~60 phút cho Camera trong ~480 phút/tháng cho 8 PLO/kênh [PB7 Mục 2, 4]
- pham vi: Toàn bộ dịch vụ tại tỉnh; xử lý Loại 3 và Loại 5 thuộc thẩm quyền Lãnh đạo VNPT T/TP
## War room cấp VNPT T/TP (Camera) — chủ trì: Trưởng PLO cấp Tỉnh — Hằng tuần [PB2 Mục 4; PB6 Mục 4; PB5 Mục 4; PB7 Mục 4]
- thanh phan: GĐ VNPT KV, GĐ TTVT KV; GĐ TT CSKH khi có Service Recovery/CSAT bất thường; PGĐ BRCĐ khi escalation Loại 2 trở lên
## War room cấp VNPT khu vực — chủ trì: Giám đốc VNPT KV — Hằng ngày (đầu ca hoặc cuối ngày) [PB2 Mục 4 (Phần IX, D.1.c.1)]
- thanh phan: Lãnh đạo VNPT KV, NVKD
- du lieu: Dashboard theo địa bàn/khu vực
- 10' Tổng quan mục tiêu: doanh thu PTM Camera, doanh thu bán hàng, TB Camera PTM trong ngày
- 30' Đi sâu đèn đỏ/vàng: khách tiềm năng, kịch bản bán hàng, đơn chưa xử lý
- 15' Quyết định: phân công NVKD trong phạm vi được giao
- 5' Giao việc & chốt deadline: giao theo phiếu qua App Employee
## War room cấp TTVT khu vực — chủ trì: Giám đốc TTVT KV — Hằng ngày [PB6 Mục 4 (Phần IX, D.1.c.2)]
- thanh phan: Lãnh đạo TTVT KV, NVKT
- du lieu: Dashboard theo địa bàn/khu vực
- 10' Tổng quan: doanh thu Camera duy trì, số phiếu tiếp xúc B2A
- 30' Đi sâu đèn đỏ/vàng: đơn chưa xử lý, phiếu lắp/sửa/bảo dưỡng tồn trong ngày theo ô địa bàn
- 15' Quyết định: phân công NVKT
- 5' Giao việc & chốt deadline qua App Employee
## War room cấp TT CSKH — chủ trì: Giám đốc TT CSKH — Hằng ngày [PB5 Mục 4 (Phần IX, D.1.c.3)]
- thanh phan: Lãnh đạo TT CSKH, Nhân viên OB (xem khoang_trong K3)
- du lieu: Tỷ lệ hoàn thành cuộc gọi chủ động (gia hạn ĐTC, 30 ngày đầu, AI Churn); phiếu khiếu nại tồn theo SLA; CSAT trong ngày
- 10' Tổng quan mục tiêu
- 30' Đi sâu đèn đỏ/vàng: khiếu nại quá SLA, khách AI Churn chưa liên hệ, phiếu bồi thường/hoàn tiền tồn
- 15' Quyết định: phân công NV OB xử lý cuộc gọi/khiếu nại ưu tiên
- 5' Chốt deadline liên hệ/xử lý trong ngày

## 4. Chuỗi báo cáo / leo thang

- Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) (chưa có playbook) → Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ → War room cấp Toàn quốc
- Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ → War room cấp Toàn quốc
- Giám đốc VNPT khu vực → Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) (chưa có playbook) → Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ → War room cấp Toàn quốc
- Giám đốc TTVT khu vực → Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) (chưa có playbook) → Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ → War room cấp Toàn quốc
- Giám đốc Trung tâm CSKH (TT CSKH) → Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) (chưa có playbook) → Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ → War room cấp Toàn quốc
- Nhân viên kinh doanh (NVKD) → Giám đốc VNPT khu vực → Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) (chưa có playbook) → Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ → War room cấp Toàn quốc
- Nhân viên kỹ thuật (NVKT) → Giám đốc TTVT khu vực → Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) (chưa có playbook) → Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ → War room cấp Toàn quốc
- Nhân viên OB (TT CSKH) → Giám đốc Trung tâm CSKH (TT CSKH) → Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) (chưa có playbook) → Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ → War room cấp Toàn quốc

## 5. Cây chẩn đoán — chỉ số lệch thì kiểm gì, ai xử lý

| Chỉ số | Kiểm gì | Ai xử lý | Việc cụ thể | Nguồn |
|---|---|---|---|---|
| Sản lượng PTM lệch mục tiêu | Kiểm tra nguồn khách hàng tiềm năng — có đủ đơn được phân giao không? | Lãnh đạo VNPT KV / TTVT KV | Rà nguồn đơn hàng; yêu cầu bổ sung tập khách tiềm năng | PB2 Mục 7 |
| Sản lượng PTM lệch mục tiêu | Kiểm tra phễu bán hàng — nghẽn ở bước nào? (áp dụng cả kênh NVKT) | Lãnh đạo VNPT KV / TTVT KV | Đối chiếu 5 bước phễu B2A (xem khoang_trong K4); kiểm tra tuân thủ kịch bản tư vấn; dự giờ, nghe lại ca tư vấn mẫu; đào tạo lại | PB2 Mục 7; PB6 Mục 7 |
| Tỷ lệ Giữ khách giảm | Kiểm tra SLA xử lý báo hỏng — có chậm không? Cảnh báo AI Churn có đúng không? | Lãnh đạo TTVT KV phối hợp Giám đốc TT CSKH | Rà phiếu báo hỏng tồn quá SLA 72 giờ theo từng NVKT; đối chiếu độ chính xác AI Churn với tỷ lệ rời mạng thực tế | PB6 Mục 7; PB5 Mục 7 |
| CSAT giảm | Kiểm tra thời gian xử lý sự cố, tỷ lệ B2A làm phiền quá mức | Lãnh đạo TTVT KV phối hợp Trưởng PLO cấp Tỉnh | (chi tiết chưa có trong 7 playbook) | PB6 Mục 7 |
| Doanh thu lệch mục tiêu | Kiểm tra nợ cước — thuê bao trả sau không thanh toán đúng hạn tăng bất thường không? | Giám đốc TT CSKH phối hợp Trưởng PLO cấp Tỉnh | (chi tiết chưa có trong 7 playbook) | PB5 Mục 7 |

Lưu ý K8: cây chẩn đoán đầy đủ (Phần IX, Mục C) chưa có; bảng trên ghép từ các playbook.

## 6. Luồng nghiệp vụ → vị trí phụ trách/thực thi

| Luồng | Tên | Vị trí | Nguồn |
|---|---|---|---|
| 2.1 | Tiếp nhận nhu cầu đa kênh – Inbound | Giám đốc VNPT khu vực; Nhân viên kinh doanh (NVKD) | PB2 Mục 2; PB3 Mục 2 |
| 2.2 | Tư vấn & Chốt đơn | Giám đốc VNPT khu vực; Nhân viên kinh doanh (NVKD) | PB2 Mục 2; PB3 Mục 2 |
| 2.3 | Ký Hợp đồng | Giám đốc VNPT khu vực; Nhân viên kinh doanh (NVKD) | PB2 Mục 2; PB3 Mục 2 |
| 2.4 | Phễu bán hàng PTM Fiber mới | Giám đốc VNPT khu vực; Nhân viên kinh doanh (NVKD) | PB2 Mục 2; PB3 Mục 2 |
| 2.5 | B2A Cross-sell trên Fiber hiện hữu | Giám đốc VNPT khu vực; Nhân viên kinh doanh (NVKD) | PB2 Mục 2; PB3 Mục 2 |
| 2.5.a | B2A Cross-sell trên Fiber hiện hữu (nhánh a) | Giám đốc VNPT khu vực; Nhân viên kinh doanh (NVKD) | PB2 Mục 2; PB3 Mục 2 |
| 2.6 | Quản trị Giá Combo | Giám đốc VNPT khu vực; Nhân viên kinh doanh (NVKD) | PB2 Mục 2; PB3 Mục 2 |
| 2.7 | Đặt hàng Multi-product/Combo | Giám đốc VNPT khu vực; Nhân viên kinh doanh (NVKD) | PB2 Mục 2; PB3 Mục 2 |
| 2.8 | (tên chưa có trong 7 playbook) | Nhân viên kinh doanh (NVKD) | PB3 Mục 2 |
| 2.9 | (tên chưa có trong 7 playbook) | Nhân viên kinh doanh (NVKD) | PB3 Mục 2 |
| 2.10 | (tên chưa có trong 7 playbook) | Nhân viên kinh doanh (NVKD) | PB3 Mục 2 |
| 3.2 | Nhập kho, gắn định danh, phân bổ | Giám đốc TTVT khu vực; Nhân viên kỹ thuật (NVKT) | PB4 Mục 2; PB6 Mục 2 |
| 3.3 | Thu hồi thiết bị | Giám đốc TTVT khu vực; Nhân viên kỹ thuật (NVKT) | PB4 Mục 2; PB6 Mục 2 |
| 3.4 | Bảo hành/Đổi trả RMA | Giám đốc TTVT khu vực; Nhân viên kỹ thuật (NVKT) | PB4 Mục 2; PB6 Mục 2 |
| 4.1 | Active/Kích hoạt dịch vụ khi lắp đặt | Giám đốc TTVT khu vực; Nhân viên kỹ thuật (NVKT) | PB4 Mục 2; PB6 Mục 2 |
| 4.2 | Lắp đặt & Ký Bàn giao | Giám đốc TTVT khu vực; Nhân viên kỹ thuật (NVKT) | PB4 Mục 2; PB6 Mục 2 |
| 4.3 | Đối tác Lắp đặt Thuê ngoài (chưa triển khai) | Giám đốc TTVT khu vực | PB6 Mục 2 |
| 4.4 | Nâng cấp/Hạ cấp Gói (thực thi kỹ thuật) | Giám đốc TTVT khu vực; Nhân viên kỹ thuật (NVKT) | PB4 Mục 2; PB6 Mục 2 |
| 4.5 | Chuyển nhượng khi Chuyển nhà/Bán nhà | Giám đốc TTVT khu vực; Nhân viên kỹ thuật (NVKT) | PB4 Mục 2; PB6 Mục 2 |
| 5.1 | Gia hạn Đóng trước cước (ĐTC) | Giám đốc Trung tâm CSKH (TT CSKH); Nhân viên OB (TT CSKH) | PB5 Mục 2; PB8 Mục 2 |
| 5.2 | Chăm sóc thuê bao trả sau & khóa/mở dịch vụ | Giám đốc Trung tâm CSKH (TT CSKH); Nhân viên OB (TT CSKH) | PB5 Mục 2; PB8 Mục 2 |
| 5.3 | Xử lý báo hỏng/sự cố kỹ thuật đúng SLA | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 5.4 | Chăm sóc chủ động & cảnh báo rời mạng AI Churn | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 5.5 | Chăm sóc chủ động 30 ngày đầu | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 5.6 | Vòng đời khi 1 phần Combo bị hủy | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 5.7 | Thanh lý/gia hạn khi hết hạn cam kết | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 5.8 | Bồi thường/Hoàn tiền Chính thức | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 5.9 | Tiếp nhận & Xử lý Khiếu nại Chính thức | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 5.10 | Thông báo thay đổi chính sách/giá/gói cước | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 5.11 | Thông báo chủ động khi có sự cố kỹ thuật diện rộng | Giám đốc Trung tâm CSKH (TT CSKH) | PB5 Mục 2 |
| 8.1 | An toàn bảo mật dữ liệu hình ảnh — rủi ro cao nhất trong 56 luồng; luôn Loại 4; ghi T0 ≤ 1 giờ | Giám đốc TTVT khu vực; Nhân viên kỹ thuật (NVKT) | PB4 Mục 2; PB6 Mục 2 |

Luồng 8.1 luôn là Loại 4: escalation ngay, ghi T0 ≤ 1 giờ, không chờ lịch họp.

## 7. Nguyên tắc chung (áp cho mọi vị trí)

- Không vị trí nào trong 7 playbook được tự đặt giá/ưu đãi ngoài chính sách đã ban hành; chính sách giá/sản phẩm Camera toàn quốc đưa lên War room Toàn quốc (Loại 5). [PB2, PB3, PB5, PB8 Mục 5/7; PB7 Mục 5]
- Từ chối 3 lần liên tiếp → hệ thống dừng chu kỳ tiếp cận (B2A và gọi chăm sóc). [PB4 Mục 2.3; PB5 Mục 5]
- Kết quả tiếp xúc B2A không được sửa sau khi đã tính vào báo cáo kỳ. [PB4 Mục 2.3, 7]
- Luồng 8.1 luôn là Loại 4, ghi T0 ≤ 1 giờ, không chờ lịch họp. [PB4 Mục 2.4; PB6 Mục 2; PB7 Mục 5]
- Vấn đề vượt phạm vi cấp khu vực báo lên War room Tỉnh/TP. [PB2, PB5, PB6 Mục 7]
- Trưởng PLO cấp Tỉnh có quyền điều hành thật (giao việc, đánh giá, họp thường xuyên) với VNPT KV, TTVT KV và TT CSKH — không chỉ phối hợp. [PB2 Mục 7; PB5 Mục 6]

## 8. Khoảng trống / mâu thuẫn K1–K8

K1: Chưa có Playbook số 1 'Trưởng PLO cấp Tỉnh' dù 6/7 playbook dẫn chiếu tới nó (thẩm quyền Loại 1, hạn mức ủy quyền, agenda War room Tỉnh, 4 chỉ số cấp Tỉnh). Mọi câu trả lời về vị trí này chỉ là ghép từ playbook khác.
K2: Người chủ trì War room Toàn quốc: PB7 Mục 4 ghi PTGĐ VNPT VinaPhone. Bộ mẫu điều hành 10/10/2026 cũng ghi Phó Tổng Giám đốc chủ trì phiên thứ Năm; theo thông tin nội bộ của người dùng (31/10/2026), phiên thứ Năm hằng tuần do Trưởng PLO Camera toàn quốc chủ trì, PTGĐ chỉ dự phiên tháng nhiều PLO. Cần VNP xác nhận đây là một hay hai phiên.
K3: PB5 Mục 4 ghi thành phần bắt buộc War room TT CSKH gồm Nhân viên OB, nhưng cùng mục và PB8 Mục 4 ghi đội OB không tham dự War room. Cần VNP thống nhất.
K4: Số bước B2A không thống nhất: PB3/PB4 ghi quy trình 4 bước (xác định điểm chạm → tiếp xúc → ghi nhận → chuyển đổi); PB2 Mục 7 ghi 'đối chiếu 5 bước phễu B2A'.
K5: Đầu mối OB chuyển tiếp: PB5 ghi 'Điện thoại viên 18001166/Giám đốc TT CSKH'; PB8 chỉ ghi 'Lãnh đạo TT CSKH'.
K6: Phạm vi luồng bán hàng: NVKD thực thi 2.1–2.10 (PB3) nhưng GĐ VNPT KV chỉ phụ trách 2.1–2.7 (PB2); tên luồng 2.8–2.10 chưa có trong 7 playbook.
K7: Ngưỡng đèn xanh/vàng/đỏ và hạn mức Loại 1/Loại 2 không có trong 7 playbook (các tỉnh đang tự đặt 80% hoặc 90%).
K8: Cây chẩn đoán (Phần IX, Mục C) chỉ xuất hiện từng phần qua các playbook; chưa có bản đầy đủ.
