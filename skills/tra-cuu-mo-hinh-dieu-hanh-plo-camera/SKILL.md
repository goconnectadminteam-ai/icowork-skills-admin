---
name: tra-cuu-mo-hinh-dieu-hanh-plo-camera
description: "BẮT BUỘC khi dùng skill này: đọc file SKILL.md, references/the-vi-tri.md và references/bang-tra.md trong thư mục skill TRƯỚC, KHÔNG tìm Knowledge Base/nhóm chat/hệ thống — dữ liệu chỉ có trong thư mục skill. Tra cứu và giải thích mô hình điều hành GTM PLO Camera theo bộ Playbook vận hành 5 Rõ — vị trí nào làm gì, chỉ số nào, luồng nghiệp vụ nào, họp war room nào (chủ trì, nhịp, agenda 10–30–15–5), quyền quyết định và 5 loại quyết định, báo cáo/leo thang lên ai, cây chẩn đoán ai xử lý, B2A, Luồng 8.1. Dùng mỗi khi người dùng hỏi 'ai làm / ai quyết / báo ai / họp gì / thuộc luồng nào / KPI của vị trí X', cần kiểm một phiếu giao việc, kết luận phiên hay kế hoạch có giao đúng người, đúng thẩm quyền không, hoặc các skill truong-plo-camera khác cần biết đầu mối và cấp chuyển — kể cả khi người dùng không nhắc chữ 'playbook'."
---

# Mô hình điều hành GTM PLO Camera

Nguồn duy nhất: 7 playbook 5 Rõ trong `references/playbook/` và dữ liệu rút gọn `data/mo_hinh.json` — tất cả nằm NGAY TRONG thư mục skill này.
Không trả lời theo hiểu biết chung về VNPT. Không đoán. Mọi khẳng định phải có nguồn dạng `[PBn Mục x]`.

## 0. Bắt buộc trước khi trả lời

- Dữ liệu trả lời NẰM TRONG skill này. KHÔNG tìm Knowledge Base, phòng chat, danh bạ, cuộc họp, Google Drive hay tệp đính kèm — các nguồn đó không có mô hình điều hành này, tìm ở đó sẽ trả lời sai.
- Câu hỏi về một vị trí (làm gì, KPI, họp gì, quyền gì, báo ai): ĐỌC file `references/the-vi-tri.md` trong thư mục skill (có đủ thẻ 8 vị trí, kèm nguồn). Không cần chạy lệnh.
- Câu hỏi liên quan NHIỀU vị trí — việc X ai quyết / báo ai, Loại 1–5, war room (chủ trì, thành phần, agenda), chuỗi leo thang, chỉ số lệch thì kiểm gì, luồng a.b do ai phụ trách, kiểm phiếu giao việc: ĐỌC `references/bang-tra.md` (đủ dữ liệu của cả 8 vị trí trong một file, kèm nguồn).
- Chỉ khi hai file trên không có: mở playbook tương ứng trong `references/playbook/`. KHÔNG chạy script trong `scripts/` khi trả lời — mọi kết quả đã có sẵn trong hai file trên; chạy lệnh chỉ làm chậm và có thể lỗi quyền.
- Cấm trả lời "không tìm thấy tài liệu" khi chưa đọc `references/the-vi-tri.md` và `references/bang-tra.md`.

| Loại câu hỏi | Đọc mục nào trong `references/bang-tra.md` |
|---|---|
| Việc X ai được quyết / phải báo ai | 1. Việc → ai quyết |
| Loại quyết định n | 2. 5 loại quyết định |
| War room / Portfolio Review | 3. War room |
| Báo cáo / leo thang lên ai | 4. Chuỗi leo thang |
| Chỉ số lệch thì kiểm gì, ai xử lý | 5. Cây chẩn đoán |
| Luồng a.b do ai phụ trách | 6. Luồng nghiệp vụ |
| Giá ngoài chính sách, B2A, Luồng 8.1 | 7. Nguyên tắc chung |
| Điểm thiếu, mâu thuẫn | 8. Khoảng trống |

## Dữ liệu sẵn: Trưởng PLO cấp Tỉnh (dùng ngay, không cần tìm thêm)

Khi được hỏi "Trưởng PLO cấp tỉnh làm gì / KPI là gì / quyền gì / họp gì", trả lời từ thẻ dưới đây, giữ nguồn, rồi nêu lưu ý K1, K7 ở cuối:

### Trưởng PLO cấp Tỉnh (PLO Camera cấp Tỉnh) (PB1)  — CHƯA CÓ PLAYBOOK, thông tin ghép từ playbook khác
- Vai trò: CHƯA CÓ PLAYBOOK. Thông tin dưới đây chỉ ghép từ các playbook khác: do PGĐ BRCĐ ủy quyền; quyết Loại 1 trong War room Tỉnh; chủ trì War room cấp VNPT T/TP hằng tuần; quản lý trực tiếp GĐ VNPT KV, GĐ TTVT KV, GĐ TT CSKH (giao việc, đánh giá, họp thường xuyên); chủ sở hữu CX toàn trình cấp Tỉnh; escalate Loại 2 lên PGĐ BRCĐ; phụ trách trực tiếp các luồng vận hành Camera hằng ngày (Bán hàng, Inventory, Giao hàng, Chăm sóc khách hàng, CX); báo cáo định kỳ tình hình đèn đỏ/vàng lên PGĐ BRCĐ. [PB7 Mục 2, 3, 4, 7; PB2 Mục 4, 7; PB5 Mục 6]
- Quản lý trực tiếp: Giám đốc VNPT khu vực, Giám đốc TTVT khu vực, Giám đốc Trung tâm CSKH (TT CSKH)
- Mục tiêu (Rõ việc): 4 chỉ số Camera cấp Tỉnh: Sản lượng PTM Tỉnh, Doanh thu Tỉnh, Giữ khách Tỉnh, CX Tỉnh (định nghĩa chi tiết, chỉ tiêu và ngưỡng nằm ở Mục 1 Playbook số 1 — chưa có, xem K1, K7) [PB7 Mục 1]
- War room: chủ trì War room cấp VNPT T/TP (Camera); tham dự Portfolio Review cấp Tỉnh [PB2 Mục 4; PB6 Mục 4; PB7 Mục 4]
- Quyền: Vận hành Camera trong War room Tỉnh, trong hạn mức được ủy quyền → Tự quyết (Loại 1) [PB7 Mục 7]
- Quyền: Đề xuất vượt hạn mức ủy quyền → Escalate PGĐ BRCĐ phê duyệt async 24–48h (Loại 2) [PB7 Mục 2, 5]
- Vượt thẩm quyền báo: Phó Giám đốc VNPT T/TP phụ trách dịch vụ BRCĐ
- Khoảng trống: Chưa có Playbook số 1 'Trưởng PLO cấp Tỉnh' dù 6/7 playbook dẫn chiếu tới nó (thẩm quyền Loại 1, hạn mức ủy quyền, agenda War room Tỉnh, 4 chỉ số cấp Tỉnh). Mọi câu trả lời về vị trí này chỉ là ghép từ playbook khác.
- Khoảng trống: Ngưỡng đèn xanh/vàng/đỏ và hạn mức Loại 1/Loại 2 không có trong 7 playbook (các tỉnh đang tự đặt 80% hoặc 90%).

## 1. Quy trình trả lời

1. Xác định loại câu hỏi rồi đọc đúng mục trong `the-vi-tri.md` / `bang-tra.md` (bảng ở mục 0). Bảng lệnh dưới đây chỉ dành cho người bảo trì chạy tay trên máy có Python, mô hình không cần chạy:

| Câu hỏi | Lệnh |
|---|---|
| Vị trí X làm gì, KPI gì, họp gì, quyền gì | `python scripts/tra_cuu.py --vi-tri <tên hoặc mã>` |
| Việc Y ai được quyết / phải báo ai | `python scripts/tra_cuu.py --ai-quyet "<việc>"` |
| Loại quyết định n | `python scripts/tra_cuu.py --loai <1-5>` |
| Luồng a.b do ai phụ trách | `python scripts/tra_cuu.py --luong <a.b>` |
| War room / Portfolio Review | `python scripts/tra_cuu.py --war-room [từ khóa]` |
| Chuỗi báo cáo, leo thang | `python scripts/tra_cuu.py --leo-thang <vị trí>` |
| Chỉ số lệch thì kiểm gì, ai xử lý | `python scripts/tra_cuu.py --chan-doan "<chỉ số>"` |
| Câu hỏi khác | `python scripts/tra_cuu.py --tim "<từ khóa>"` |
| Bức tranh tổng thể | đọc `references/tong-quan.md` |

2. Nếu kết quả chưa đủ, mở đúng một file playbook trong `references/playbook/` ở mục được chỉ ra.
3. Trả lời ngắn, theo thứ tự: **câu trả lời → căn cứ [PBn Mục x] → lưu ý (nếu có)**.
4. Nếu câu trả lời chạm tới vị trí Trưởng PLO cấp Tỉnh, ngưỡng đèn, hạn mức Loại 1/2, hoặc một điểm mâu thuẫn: chạy `--khoang-trong` và nêu mã K tương ứng.
5. Đã chạy lệnh mà vẫn không tìm thấy trong 7 playbook (và `data/mo_hinh.json`): trả lời "Chưa có trong 7 playbook" và nói tài liệu nào có thể có (thường là Playbook số 1 "Trưởng PLO cấp Tỉnh" hoặc "Bản Tổ chức triển khai, quản trị PLO Camera", Phần IX–X). Không lấp chỗ trống bằng suy luận.

## 2. Kiểm một văn bản theo mô hình (phiếu giao việc, kết luận phiên, kế hoạch)

Với mỗi việc trong văn bản, đối chiếu và báo theo dạng `Việc │ Người được giao │ Đúng/Sai │ Lý do [nguồn]`:
- Người được giao có đúng vị trí giữ luồng/chỉ số đó không (`--luong`, `--vi-tri`).
- Việc có vượt quyền của người đó không (`--ai-quyet`); nếu vượt, phải là đề xuất/escalate lên ai, loại mấy (`--loai`).
- Việc có giao cho vị trí không dự war room đó không (ví dụ giao NV OB qua War room Tỉnh).
- Việc liên quan giá/ưu đãi ngoài chính sách, sửa kết quả B2A đã tính kỳ, hay Luồng 8.1 không theo Loại 4 → luôn là Sai.
Chỉ nêu Sai khi có căn cứ trong playbook. Chỗ playbook không quy định → ghi "chưa quy định", không ghi Sai.

## 3. Quy tắc diễn đạt

- Dùng chức danh như trong playbook, không dùng tên người.
- Giữ nguyên thuật ngữ gốc: B2A, GHTT, ĐTC, PSSL, Service Recovery, AI Churn, Portfolio Review, Loại 1–5, Luồng a.b.
- Phân biệt rõ "theo playbook" với "đề xuất – cần xác nhận chính thức". Không biến đề xuất thành quy định.
- Không viết lại, tóm tắt sai hay đổi số trong playbook (ví dụ 24–48 giờ, SLA 72 giờ, T0 ≤ 1 giờ, 3 lần từ chối, 10–30–15–5 phút).

## 4. Dùng cùng các skill khác

- `truong-plo-camera-chan-doan-lech`: lấy đầu mối và cấp chuyển ở đây khi bảng định tuyến của skill đó chưa có.
- `truong-plo-camera-soan-tin-nhan`, `-ke-hoach-hanh-dong`, `-ket-luan-phien`: dùng mục 2 để kiểm phần "Ai (chức danh)" và "Chuyển cấp".
