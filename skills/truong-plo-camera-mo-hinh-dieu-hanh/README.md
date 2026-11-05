# Cài và chạy thử — truong-plo-camera-mo-hinh-dieu-hanh (v1, 03/11/2026)

Skill tra cứu mô hình điều hành GTM PLO Camera từ 7 Playbook vận hành 5 Rõ (vị trí số 2–8).

## Cài vào opencode
Chép cả thư mục vào `.opencode/skills/truong-plo-camera-mo-hinh-dieu-hanh/`. Chỉ cần Python 3 chuẩn.

## Kiểm dữ liệu (không cần mô hình)
```
python scripts/tu_kiem.py          # 14/14 đạt
python scripts/tra_cuu.py --danh-sach
python scripts/tra_cuu.py --khoang-trong
```

## Chạy thử với Qwen
Hỏi lần lượt các câu trong `examples/cau-hoi-mau.md`. Đạt khi đúng ý và có nguồn [PBn Mục x].
Thử thêm ca kiểm phiếu giao việc ở cuối file đó.

## Cập nhật khi có playbook mới
1. Chuyển file Word sang Markdown: `pandoc <file>.docx -t gfm --wrap=none -o references/playbook/<số>-<ten>.md`
2. Thêm/sửa mục tương ứng trong `data/mo_hinh.json` (vị trí, quyền, war room, luồng).
3. Sinh lại file cho mô hình đọc: `python scripts/sinh_tai_lieu.py` (ghi đè `references/the-vi-tri.md` và `references/bang-tra.md`); cập nhật khối "Dữ liệu sẵn" trong SKILL.md nếu thẻ Trưởng PLO cấp Tỉnh đổi.
4. Thêm câu kiểm vào `scripts/tu_kiem.py` và `examples/cau-hoi-mau.md`, chạy lại `tu_kiem.py`.

## Phạm vi bản này
- Có: 7 playbook (PGĐ BRCĐ, GĐ VNPT KV, NVKD, NVKT, GĐ TT CSKH, GĐ TTVT KV, NV OB).
- Chưa có: Playbook số 1 "Trưởng PLO cấp Tỉnh"; Trưởng PLO Camera toàn quốc; Chuyên viên ĐHKD; Chuyên viên Quản lý Thiết bị & Đối soát; bản đầy đủ Phần IX–X của tài liệu gốc.
- 8 khoảng trống/mâu thuẫn ghi trong `data/mo_hinh.json` → `khoang_trong` (K1–K8).
