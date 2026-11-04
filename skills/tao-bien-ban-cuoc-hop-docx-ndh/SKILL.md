---
name: tao-bien-ban-cuoc-hop-docx-ndh
description: |
  - Tạo Biên bản cuộc họp đúng mẫu MeetingMinutes. Xuất file Docx
  - Input: Nhập text mô tả hoặc đính kèm file <20KB
  - Output: File docx Biên bản họp
---

# Tạo Biên bản cuộc họp (mẫu MeetingMinutes) — bản cho agent context nhỏ

## ⚠️ Quy tắc bắt buộc
1. **Nội dung file = toàn văn biên bản.** CẤM ghi đường dẫn, link `file://`, tên file hay câu "đã tạo file…" vào nội dung file.
2. Trước khi gọi tool ghi/tạo file, tự kiểm tham số nội dung: là **văn bản biên bản** (Markdown/HTML), KHÔNG phải đường dẫn; `p1.md`/biên bản đầy đủ phải bắt đầu bằng `# BIÊN BẢN CUỘC HỌP` (HTML: `<html>`). Sai → viết lại, không gọi tool.
3. **Không đọc nguyên file Word/PDF đính kèm vào context.** Luôn trích văn bản gọn rồi đọc theo phần (Bước 1).
4. Không đọc file trong `assets/` trừ khi bước nào yêu cầu. Không thêm dòng lưu ý/disclaimer "Nội dung được tổng hợp từ AI…".

## Lệnh Python: chỉ dùng đúng dạng này
`<S>` là thư mục chứa tệp này: chép nguyên văn đường dẫn ở dòng "Base directory for this skill" ngay sau nội dung skill, trong ngoặc kép (Windows dùng `python`). **Không** `ls`/`dir`/`find` để tìm skill, **không** `cd`, **không** gõ đường dẫn Python nào khác và **không** `pip install`: script tự cài thư viện thiếu. Script in `=== DỪNG … ===` thì làm đúng câu đó (thường là chuyển Cách B/C), không tự bịa nội dung.

## Bước 1 — Đọc input tiết kiệm context
- **Chạy được Python:** `python3 "<S>/scripts/extract_text.py" "<file_input>"` → in số ký tự và số phần (mỗi phần 10.000 ký tự). 1 phần: đã in toàn văn, dùng luôn.
  - **File lớn (>2 phần, ví dụ tóm tắt GoMeet theo dòng thời gian dài):** KHÔNG đọc hết từng phần. Chạy `python3 "<S>/scripts/extract_text.py" "<file_input>" --tom-gon` (thường còn 1–2 phần): mỗi mục một dòng `[giờ] Tiêu đề: ý chính`, giữ nguyên các ý có việc cần làm, người phụ trách, hạn, quyết định, rủi ro. Biên bản chỉ ≤ 700 từ nên bản gọn là đủ; chỉ chạy lại không có `--tom-gon` kèm `--chunk N` khi cần chi tiết một đoạn cụ thể.
  - Sau MỖI phần chỉ ghi lại **ghi chú ≤ 8 dòng** (quyết định, việc cần làm + người + hạn, rủi ro, số liệu chính) rồi bỏ qua văn bản gốc. Biên bản viết từ các ghi chú này.
- **Không chạy được Python:** dùng tool đọc file của agent, đọc từng đoạn (nếu tool hỗ trợ phân trang/giới hạn), ghi chú ngắn sau mỗi đoạn như trên.
- Text dán trực tiếp: dùng luôn. Transcript sai chính tả → hiểu theo ngữ cảnh. Không hỏi lại trừ khi không có nội dung.

## Bước 2 — Viết Markdown NGẮN, chia 2 phần
Quy tắc: bullet 3–5 ý, mỗi ý ≤ 20 từ; mỗi bảng 3–5 dòng, mỗi ô ≤ 15 từ; ưu tiên chỉ `Cao`/`Trung bình`/`Thấp`; thiếu → `-`; **không bịa** — ID/giờ/số người không có thì ghi `[điền …]`. Toàn biên bản ≤ 700 từ.

**Phần 1 — `p1.md`:**
```markdown
# BIÊN BẢN CUỘC HỌP

## I. Thông tin
- ID: <…>
- Phiên họp: <…>
- Ngày: <dd/mm/yyyy>
- Thời gian: <HH:MM - HH:MM>
- Số người tham dự: <…>

## II. Nội dung

### Tóm tắt cuộc họp
<1 đoạn 3–4 câu>

### Mục tiêu cuộc họp
- <…>

### Các vấn đề chính được thảo luận
- <Chủ đề: chi tiết ngắn>

### Các quyết định hoặc kết luận đã được thống nhất
- <…>
```
**Phần 2 — `p2.md`:**
```markdown
### Các nội dung chính
| STT | Chủ đề | Nội dung |
| --- | --- | --- |
| 1 | <…> | <…> |

### Danh sách hành động
| STT | Công việc | Người phụ trách | Người phối hợp | Mức độ ưu tiên | Thời hạn | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | <…> | <…> | <…/-> | <Cao/Trung bình/Thấp> | <…/-> | <…/-> |

### Tổng hợp rủi ro, khó khăn hoặc phụ thuộc
| Vấn đề | Ảnh hưởng | Người xử lý | Kết quả đầu ra |
| --- | --- | --- | --- |
| <…> | <…> | <…> | <…> |
```
Mục **"Danh sách công việc phân theo người phụ trách" KHÔNG cần viết** — script tự sinh từ bảng hành động. (Cách B/C: tự thêm mục này cuối biên bản, dạng `**Tên**` + `- Việc (Ưu tiên: …, Thời hạn: …)`.)
Có cả transcript lẫn timeline → mỗi nguồn 1 khối, mở đầu `### A. Nội dung tổng hợp từ transcript (STT)` / `### B. Nội dung tổng hợp từ dòng thời gian (Timeline)` (sau `## II. Nội dung`).

## Bước 3 — Xuất file (chọn cách ĐẦU TIÊN làm được)
Tên file: `BienBanHop_<TenPhienHopKhongDau>_<ddmmyyyy>`.
- **Cách A — chạy được Python:** ghi `p1.md`, `p2.md` (2 lần ghi riêng), rồi:
  `python3 "<S>/scripts/md_to_docx.py" p1.md p2.md BienBanHop_xxx.docx --xoa-nhap` (thêm `--xoa-nhap` để xoá p1.md, p2.md sau khi tạo xong, thư mục chỉ còn file kết quả).
  Script báo `LỖI` nếu nội dung rỗng/là đường dẫn → sửa file .md, chạy lại.
- **Cách B — có tool tạo Word/docx từ nội dung:** truyền **nguyên văn p1 + p2 + mục phân theo người** vào tham số nội dung; tên `.docx` vào tham số tên/đường dẫn. Không truyền đường dẫn file .md thay cho nội dung.
- **Cách C — chỉ có tool ghi file văn bản:** đọc `assets/cach_c_html.md` và làm theo (ghi HTML đuôi `.doc`).

## Bước 4 — Kiểm tra & trả lời
- Đọc lại file vừa tạo (Cách A: dòng `Đã tạo: … (N ký tự)` với N > 500). Nếu nội dung chỉ là đường dẫn/trống → làm lại Bước 3 bằng cách tiếp theo.
- Trả lời chat 1–2 câu: link/tên file, số việc cần làm, các ô `[điền …]` cần bổ sung. Không in lại biên bản. Dùng Cách C thì nói rõ file là `.doc` (Word mở được), không gọi là docx.
- Input là file Word cũ `.doc` nhị phân mà script báo không đọc được: bảo người dùng lưu thành `.docx` hoặc dán nội dung; không đoán nội dung.
