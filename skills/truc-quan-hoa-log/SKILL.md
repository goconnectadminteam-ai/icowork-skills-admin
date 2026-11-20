---
name: truc-quan-hoa-log
description: |
  - Đọc file log Langfuse (trace-*.json, xuất từ iWork/opencode hoặc OpenAI-generation) và vẽ thành ảnh dòng thời gian (PNG + HTML): từng lượt model, từng lần gọi tool, token, thời gian
  - Tự đánh dấu dấu hiệu lỗi: ngữ cảnh bị nén, tràn context, tool bị từ chối quyền, vòng lặp suy nghĩ, chạm trần reasoning, lượt kết thúc không có báo cáo
  - Viết phần "Vì sao lỗi" bằng tiếng Việt cho người không rành kỹ thuật
  - Input: file .json log Langfuse (một hoặc nhiều). Output: ảnh PNG + HTML + diễn giải nguyên nhân
---

# Trực quan hóa log

Việc đọc và vẽ log do **script** làm (ổn định, không phụ thuộc model đọc 180 KB JSON). Bạn chỉ làm hai việc: chạy script, rồi **diễn giải nguyên nhân** dựa trên kết quả script in ra.

## Bước 1. Kiểm tra đầu vào

Skill chỉ dành cho file log Langfuse: JSON có khoá `trace` và `observations`. Nếu người dùng đưa thứ khác (PDF, Word, ảnh chụp màn hình, log văn bản thường, JSON không có hai khoá trên) thì **dừng, nói rõ skill này không dùng được cho tệp đó** và gợi ý tệp đúng (xuất trace từ Langfuse: Trace → Download JSON). Không tự bịa timeline.

## Bước 2. Chạy script (một lệnh)

```text
python3 "SKILL_DIR/scripts/trace_viz.py" "INPUT.json" --out "trace-viz-output"
```

`SKILL_DIR` là thư mục chứa tệp này; Windows dùng `python`. Nhiều file thì chạy mỗi file một lần. Tuỳ chọn: `--tz 7` (múi giờ hiển thị, mặc định UTC+7), `--no-png` (chỉ HTML).

Script tạo `trace-viz-output/trace-<8 ký tự id>.html` và `.png`, và in ra: yêu cầu của người dùng, các bước, **DẤU HIỆU**, **CHUỖI NGUYÊN NHÂN suy từ luật**. Chỉ dùng Chrome hoặc Edge để xuất PNG; thiếu thì vẫn có HTML, hãy nói rõ cần cài Chrome (https://www.google.com/chrome/) nếu người dùng muốn ảnh.

## Bước 3. Diễn giải "Vì sao lỗi"

Dựa vào phần DẤU HIỆU và CHUỖI NGUYÊN NHÂN script in ra, viết 3-5 ý đánh số, theo thứ tự nhân quả (cái gì xảy ra trước dẫn tới cái gì). **Mỗi ý có hai phần: nguyên nhân (một câu) và "Cách khắc phục:" (một câu).** Quy tắc:

- Chỉ khẳng định điều log chứng minh được (số token, thời gian, trạng thái tool, thông báo lỗi). Log iWork **không chứa nội dung kết quả tool**, nên không đoán dữ liệu bên trong.
- **Bắt buộc** viết "nhiều khả năng" cho điều chỉ suy ra từ luật, không có bằng chứng trực tiếp trong log: "ngữ cảnh bị nén" (suy từ token vào tụt mạnh), "model loay hoay", "kết quả tool quá lớn". Chỉ nói chắc những gì log ghi thẳng: lỗi tool, thông báo từ chối, số token, thời gian.
- Nêu **cách khắc phục** cho từng nguyên nhân (vd: giảm kích thước kết quả tool, cấp quyền trước cho lệnh cần chạy, thêm điều kiện dừng cho vòng lặp).
- Dấu hiệu `INFO` (vd gọi cùng một tool nhiều lần) chỉ là gợi ý, đừng coi là lỗi.
- Không có dấu hiệu nào: nói lượt chạy bình thường theo các luật hiện có, không bịa lỗi.

## Bước 4. Trả kết quả

Trả đường dẫn PNG và HTML (dạng link markdown), rồi phần "Vì sao lỗi". Nếu muốn chèn diễn giải của bạn vào ảnh thì không sửa HTML bằng tay; phần "Vì sao lỗi" trong ảnh là bản suy từ luật, bản của bạn nằm trong câu trả lời.

## Các dấu hiệu script nhận ra

| Dấu hiệu | Cách nhận | Mức |
|---|---|---|
| Ngữ cảnh bị nén | token vào giảm ≥40% so với lượt model trước (lượt trước ≥20k) | cảnh báo |
| Ngữ cảnh lớn | đỉnh token vào ≥50k | cảnh báo |
| Tool bị từ chối / lỗi | observation `level=ERROR` (từ chối nếu thông báo có "permission") | lỗi |
| Chạm trần reasoning | reasoning ≥16.384 token mà output = 0 | lỗi |
| Vòng lặp suy nghĩ | ≥30% câu trong phần suy nghĩ bị lặp | lỗi |
| Kết thúc không có báo cáo | output cuối trống hoặc chỉ còn tool_call chưa chạy | lỗi |
| Lượt model chậm | ≥20 giây | cảnh báo |
| Gọi tool lặp | cùng một tool ≥6 lần liên tiếp | thông tin |

Ngưỡng nằm ở đầu `scripts/trace_viz.py`, chỉnh tại đó.

## Giới hạn đã biết

- Định dạng opencode (iWork) cho input/output ở mức trace, không có từng tool; `bash` bị từ chối chỉ lấy được lệnh khi nó là tool_call cuối của trace.
- Chưa đo "dùng skill không phù hợp yêu cầu" (cần nội dung skill và yêu cầu để so khớp); đó là việc của một bước kiểm đầu vào riêng.
