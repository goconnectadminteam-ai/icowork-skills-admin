# Cách C — Ghi biên bản dạng HTML, lưu đuôi .doc (Word mở được)

Dùng khi agent KHÔNG chạy được Python và KHÔNG có tool tạo docx. Ghi file `BienBanHop_xxx.doc` với nội dung HTML dưới đây, chuyển TOÀN BỘ Markdown biên bản sang HTML (bullet → `<ul><li>`, bảng → `<table border="1">`, `**Tên**` → `<p><b>Tên</b></p>`). Nếu nội dung dài, ghi làm nhiều lần (append) theo từng mục.

```html
<html><head><meta charset="utf-8"><style>
body{font-family:'Times New Roman';font-size:12pt;line-height:1.5}
h1{font-size:16pt;text-align:center} h2,h3{font-size:14pt} th{background:#f8fafc}
</style></head><body>
<h1 align="center">BIÊN BẢN CUỘC HỌP</h1>
<h2>I. Thông tin</h2>
<table border="0" style="margin-left:24pt"><tr><td width="160"><b>- ID:</b></td><td>…</td></tr> … </table>
<h2>II. Nội dung</h2><h3>Tóm tắt cuộc họp</h3><p>…</p>
<h3>Mục tiêu cuộc họp</h3><ul><li>…</li></ul>
<h3>Các nội dung chính</h3>
<table border="1" cellspacing="0" cellpadding="6" width="100%" bordercolor="#cbd5e1">
<tr bgcolor="#f8fafc"><th align="left">STT</th><th align="left">Chủ đề</th><th align="left">Nội dung</th></tr>
<tr><td>1</td><td>…</td><td>…</td></tr></table>
… (chuyển TOÀN BỘ Markdown Bước 2 sang HTML theo cùng cách; [điền …] → <span style="background:yellow">[điền …]</span>)
</body></html>
```
