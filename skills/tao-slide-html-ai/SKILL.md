---
name: tao-slide-html-ai
description: |
  - Chuyển nội dung báo cáo thành slide trình chiếu. Xuất file HTML
  - So sánh hai kỳ (vd tuần 4 và tuần 5): có điểm tiến bộ, điểm cần chú ý, mới/hết và số liệu cần đối chiếu
  - Input: Báo cáo, số liệu, dàn ý
  - Output: Slide HTML
---

# Báo cáo điều hành dạng slide (giao diện K7 chung)

Bạn viết **nội dung** từng slide (JSON). Driver `iwork.py` lo phần còn lại: trích nguồn, kiểm số liệu, ghép, render HTML bằng khung K7 khoá sẵn, tự kiểm chất lượng và giao. Dùng model mặc định của iWork; không gọi API riêng.

## Bắt đầu ngay, không hỏi

Người dùng chỉ chọn skill và đính kèm tệp; lời nhắn có thể chỉ là "Mở <tên skill>". **Đó đã là yêu cầu đầy đủ.** Chạy `start` NGAY với tệp đính kèm (đường dẫn tương đối iWork liệt kê). Không hỏi tệp nào, ngày, phạm vi hay có muốn bắt đầu không, và không trả lời bằng lời giải thích skill làm gì. Tệp chưa được trích xuất trong ngữ cảnh là bình thường: driver tự trích.

## Lệnh shell: chỉ MỘT dạng được phép

iWork hiện hộp xin quyền và **đứng chờ người dùng bấm** với mọi lệnh khác dạng dưới đây. Mỗi lần như vậy là một lần làm phiền người dùng.

```text
python3 "SKILL_DIR/iwork.py" start "INPUT" --work "report-output"     # chỉ MỘT lần, lệnh đầu tiên
python3 "report-output/advance.py"                                    # mọi lệnh sau: driver in sẵn, chạy nguyên văn
```

`SKILL_DIR` là thư mục chứa tệp này (đường dẫn tuyệt đối, trong ngoặc kép; Windows dùng `python`). Sau `start`, driver tạo `report-output/advance.py` và chỉ in lệnh dạng trên: **không bao giờ tự gõ lại đường dẫn skill** (gõ sai sẽ lỗi và bị hỏi quyền). Mọi đường dẫn khác là **tương đối**, trong ngoặc kép. **Lệnh bị từ chối hoặc báo không tìm thấy tệp:** chạy lại đúng lệnh đã in (`python3 "review-output/next.py"` / `python3 "report-output/advance.py"`). Không bao giờ kết luận "driver không có trên đĩa" hay "skill chạy trong sandbox" (sai: driver luôn có), và không tự xuất báo cáo bằng cách khác ngoài driver (kết quả đó không được kiểm).

**Ghi các tệp `parts/NN.json` thẳng vào `report-output/parts/` bằng công cụ `write`.** Không ghi vào thư mục tạm của iWork rồi chép sang bằng `Copy-Item`/`cp`/`$src`/`$dst`: lệnh có biến `$` luôn bị iWork hỏi quyền.

**Luôn có `python` (Windows) hoặc `python3` đứng trước đường dẫn tệp.** Không bao giờ chạy một đường dẫn `.py` đứng một mình (kiểu `"…\next.py"` hay `& "…\advance.py"`): Windows sẽ hiện hộp "Select an app to open this .py file" và lệnh không chạy.

CẤM:

- `cd`, `&&`, `;`, `|`, `>`, `2>/dev/null`, `$BIẾN`, `$(…)`, dấu huyền, `~`, vòng lặp, nhiều dòng.
- `python3 -c`, heredoc, tự viết script, `ls`/`cat`/`find`/`grep` trên thư mục skill. Cần xem tệp thì dùng công cụ `read`; cần ghi tệp thì dùng `write`/`edit`, không dùng shell. Muốn kiểm JSON hay đếm ký tự: chạy `advance`, driver đã báo đúng lỗi và số ký tự cần bớt.
- Đường dẫn ngoài workspace hiện tại. Tệp người dùng gửi: dùng đúng đường dẫn tương đối mà iWork liệt kê cho lượt này. `--work` luôn là `report-output` (không thêm tên thư mục phiên phía trước).

Đường dẫn `<S>` in ở dòng "Base directory for this skill" ngay sau nội dung skill này: chép nguyên văn, **không `ls`/`dir`/`find` để tìm** (liệt kê thư mục, kể cả thư mục làm việc, có thể bị iWork hỏi quyền; Windows: `dir`, `Get-ChildItem`).

## Quy tắc không được dừng

Người dùng **không được phải nhắn thêm** để skill chạy tiếp. Mọi lệnh driver kết thúc bằng một trong ba dòng:

- `=== CHƯA XONG … ===`: làm đúng việc được nêu rồi chạy lệnh tiếp **trong cùng lượt**. Ghi xong plan, vài slide hay build đạt đều **chưa phải** là xong.
- `=== DỪNG … ===`: chỉ khi tệp trạng thái bị sửa tay hoặc không có bản nào để giao. Báo đúng trạng thái. Câu đầu của trả lời là **"CHƯA tạo được file HTML"** kèm lý do một dòng; không nói đã xong, không tự dựng slide bằng tay.
- **Thiếu phần mềm** (driver in `=== DỪNG` nêu tên): nói rõ cho người dùng cần cài gì và đưa link. **Chép NGUYÊN VĂN đúng link nằm trong thông báo `=== DỪNG` của driver**, không tự nhớ, không lấy link của công cụ khác. Chỉ khi thông báo không có link mới dùng bảng dưới, và mỗi lỗi chỉ có MỘT link của chính nó. Không im lặng, không tự cài, không tự viết tay, không nói đã xong.
  - Không chạy được lệnh `python`/`python3` (cần Python 3.12) → https://www.python.org/downloads/
  - Windows báo `DLL load failed` (thiếu Microsoft Visual C++ Redistributable x64) → https://aka.ms/vs/17/release/vc_redist.x64.exe
  - Không dựng hoặc kiểm tra được HTML vì thiếu trình duyệt Google Chrome hoặc Microsoft Edge → https://www.google.com/chrome/
- **Không bịa kết quả:** chỉ nêu kết quả và tệp mà driver đã in ở `HOÀN TẤT`. Chưa có thì không tạo tệp, không tự điền nhận xét, điểm hay số liệu, không liệt kê tệp nguồn hoặc tệp trung gian như thể đó là kết quả.
- `HOÀN TẤT`: trả kết quả (xem cuối trang). Bản có chữ `BẢN NHÁP` vẫn là HOÀN TẤT: giao file và nêu rõ các cảnh báo.

Thêm:
1. **Không hỏi lại, không xin xác nhận, không đưa lựa chọn** (ngày, số slide, chương, mẫu, bỏ qua bước nào): tự quyết theo nguồn; điểm chưa chắc ghi vào `meta.canXacNhan`. Mọi lỗi driver báo đều tự sửa được rồi chạy lại.
2. **Mỗi bước chỉ làm đúng việc driver nêu, không phân tích dài.** Nghĩ lâu trên một quyết định là cách duy nhất khiến lượt bị cắt đứt giữa chừng. Thiếu chắc chắn thì chọn phương án đơn giản nhất.
3. **Không tạo tệp ngoài** `notes.md`, `plan.json`, `parts/NN.json` trong WORK; không sửa `iwork-state.json`, `job-step.json`, `report.json`. Driver tự sửa lỗi icon và số chương/số mục, tự lập bản kiểm chất lượng và tự `finish`.
4. **Bị ngắt hay nén ngữ cảnh**: đọc `notes.md`, chạy lại `advance "report-output"`; không `start` lại, không viết lại slide đã đạt.

**Sau khi bị nén ngữ cảnh hoặc người dùng bảo "làm tiếp":** việc đầu tiên là chạy `python3 "report-output/advance.py"`; lệnh này luôn đúng và làm tiếp từ chỗ dừng. Không tìm lại tệp nguồn (`ls`, `dir`, `find`), không `init`/`start` lại. **Luôn gọi công cụ bash thật.** Tuyệt đối không viết lệnh thành chữ như `[Assistant tool call]: bash(...)` trong câu trả lời: chữ đó không chạy được, lượt kết thúc và người dùng phải nhắn lại.

**Người dùng báo lỗi tệp sau khi đã `HOÀN TẤT`** (trang trắng, chữ tràn, sai số, muốn sửa chữ): đó là việc của driver, không phải của bạn tự điều tra. **Cấm** mở HTML bằng `python3 -c`, `grep`, `cat`, `fitz`: các lệnh đó bị iWork hỏi quyền và không sửa được gì. Việc đúng: nếu cần đổi chữ thì sửa `report-output/_work/parts/NN.json` bằng công cụ `edit`, rồi chạy `python3 "report-output/_work/advance.py"`. Driver tự kiểm đầu ra thật (kể cả slide trắng), tự sửa lỗi cơ học, dựng lại HTML và in `HOÀN TẤT` khi xong.

## Các bước

```text
python3 "SKILL_DIR/iwork.py" start "INPUT" --work "report-output"
```

`INPUT` là tệp người dùng gửi (nhiều tệp cùng một báo cáo thì truyền cùng lệnh). Thêm `--date DD/MM/YYYY` khi người dùng nêu ngày, `--author` khi nêu rõ đơn vị. Mặc định **chỉ tiếng Việt**; lời thoại do driver tự tổng hợp từ chữ trên slide (bạn không viết `loiThoai`); chỉ thêm `--song-ngu` khi người dùng yêu cầu bản tiếng Anh. Thiếu thư viện thì chạy lệnh cài driver in ra rồi `start` lại.

**Giao diện và logo:** skill này dùng giao diện **chung**: không logo VNPT AI, chân trang "iView"; người xem tự gắn logo bằng nút **Logo và chân trang** trong trang HTML. Cần nhận diện VNPT AI thì dùng skill `tao-slide-logo-html-ai`. Người dùng đưa tệp logo thì thêm `--logo "<tệp ảnh>"` vào `start`; muốn chữ chân trang riêng thì `--chan-trang "VNPT"`. Logo đến sau khi đã giao: chạy lại `start` cùng `--work` với `--logo`, rồi `advance`.

1. **Đọc một lần** `content.md` và `facts.md`. Bảng 12 mẫu K7 (trường, số mục, giới hạn ký tự, icon) do `start` in sẵn: **không cần đọc** [huong-dan-k7.md](references/huong-dan-k7.md), chỉ mở khi cần ví dụ. Rồi ghi **`notes.md`** (tối đa 25 dòng): thông điệp chính, ngày nguồn, số liệu cần dùng kèm vị trí, nhóm việc, hạn, kiến nghị. Đây là bộ nhớ của bạn; các lô sau không đọc lại toàn bộ nguồn.
2. **`plan.json`**: `{"meta":{"ten":"…","ban":"Bản 1 · dd/mm/yyyy","computed":[],"canXacNhan":[]},"outline":["tiêu đề slide 1","tiêu đề slide 2"]}` (`outline` là danh sách CHUỖI). Số slide theo lượng nguồn (báo cáo ngắn thường 8–12 slide, nguồn nhiều đơn vị/hạng mục thì nhiều hơn; không gộp để cho ít slide); có tiến độ/rủi ro/kiến nghị thì có slide tóm tắt điều hành. Số liệu tự tính chỉ khai trong `meta.computed` dạng `{"value","formula":"a+b"}`.
   - Có chương (nguồn chia phần rõ): ít nhất hai slide `mau:"chuong"`; slide nội dung ghi `dauMuc` chữ. Không có chương: chỉ dùng `dauMuc` chữ. **Đánh số do driver tự lo**, bạn không cần tính.
   - **Đủ thông tin, không tóm tắt quá tay.** Người xem cần đọc được nội dung chứ không chỉ tiêu đề: mỗi thẻ, bước, ý viết thành câu đầy đủ (chủ thể + con số, mốc, đơn vị có trong nguồn), không câu cụt; mỗi slide nêu hết các mục nguồn của chương đó, không gộp "Mục 2-3" vào một slide. **Không đếm ký tự khi viết** (đếm làm mất thời gian): driver tự báo nếu quá dài hoặc quá thưa. Nguồn có danh sách theo đơn vị/hạng mục/dòng theo dõi thì dùng `bang` (2–12 hàng, mỗi hàng giữ tên, số, hạn, kết quả); dùng nhiều hàng khi nguồn còn dòng, ô ngắn gọn (một dòng) để vừa khung; còn dòng thì chia sang slide kế. Tràn khung thì rút chữ trong ô hoặc chuyển bớt sang slide mới, không bỏ số liệu.
   - **Bìa là mục đích của báo cáo**, nói đúng việc người dùng nhờ (tên báo cáo/so sánh/đánh giá và đối tượng, kỳ); kết luận và số liệu nổi bật để từ slide 2 (tóm tắt điều hành), không nhét kết quả vào tiêu đề bìa.
3. **`parts/NN.json`**: driver giao từng lô tối đa 6 slide. Ghi cả lô bằng nhiều lệnh `write` **trong cùng một bước**. Mỗi tệp là một object slide có `"mau"` (1 trong 12 mẫu) và `"tieuDe"`; bìa là `01.json`; không bọc trong `slides`.
4. **`advance`** sau mỗi lô. Đủ slide thì driver tự build và kiểm (cấu trúc K7, giới hạn chữ, số có trong nguồn, nhất quán %, tên riêng, tràn chữ). Có lỗi: sửa **tất cả** lỗi trong danh sách rồi `advance`. Tràn chữ thì viết ngắn lại hoặc tách slide, không sửa khung. Hết 4 lượt build lỗi thì driver tự giao bản nháp kèm cảnh báo.
5. Build đạt thì driver **tự kiểm chất lượng và `finish`** trong cùng lệnh, rồi in `HOÀN TẤT`. Bạn không viết file kiểm. Chỉ khi driver in `BUILD ĐẠT nhưng còn … yêu cầu bao phủ` thì mở `TASK.md`, sửa slide nêu đủ mã dòng/đơn vị/hạn được liệt kê rồi `advance`.

## Hai kỳ của cùng một báo cáo (so sánh tuần này với tuần trước)

**Chỉ khi người dùng NHỜ so sánh** hai kỳ hoặc hai bản (đưa hai tệp, vd tuần 4 và tuần 5), thêm cờ `--so-sanh` vào lệnh `start`. **Không nhờ so sánh thì tuyệt đối không thêm cờ**, dù hai tệp giống nhau đến đâu (vd hai bản nháp, chỉ nhờ làm slide). Có cờ: `start` tự tạo `so-sanh.md` chỉ gồm các chỗ khác nhau và in lệnh đọc. **Đọc `so-sanh.md`, không đọc `content.md`** (hàng trăm nghìn ký tự, làm đầy ngữ cảnh rồi dừng). **Bìa nêu mục đích đúng như người dùng nhờ** (vd "So sánh tiến độ tuần 4 và tuần 5", dòng phụ: dự án và hai kỳ), không đặt kết quả hay số liệu làm tiêu đề bìa.

**Driver tự thêm (bạn không viết, không chép lại):** các bảng thay đổi (Mục | Chỉ tiêu | Kỳ trước | Kỳ này) đã so từng dòng bằng code; bảng **mới hoặc hết so với kỳ trước** (vd rủi ro mới bổ sung); bảng **số liệu cần đối chiếu** (cột "tuần trước" của kỳ này lệch với kỳ trước, tỷ lệ vượt 100%, số kỳ trước còn sót trong kỳ này); bảng **chỉ đạo đã đến hạn chưa xong**. Các bảng này đặt sau slide "Điểm cần chú ý".

**Bạn chỉ viết tối đa 9 slide, theo thứ tự:**
1. Bìa.
2. Tóm tắt điều hành (mẫu `so-lieu`, 6 số chính, mỗi số kèm giá trị kỳ trước).
3. **Điểm tiến bộ** (mẫu `the`, `dauMuc` đúng chữ "Điểm tiến bộ", 3–6 thẻ): mỗi thẻ **một hạng mục khác nhau** (không dồn nhiều thẻ vào cùng một phần mềm; các giai đoạn của một hệ thống gộp trong một thẻ), viết "tăng từ A lên B", lấy từ mục TĂNG MẠNH NHẤT và các việc đã hoàn thành trong `so-sanh.md`.
4. **Điểm cần chú ý** (mẫu `the`, `dauMuc` đúng chữ "Điểm cần chú ý", 6 thẻ, mỗi thẻ một câu đầy đủ nêu hạng mục và số cụ thể, gồm cả điều không đổi nhưng đáng chú ý như hạn, giải ngân). `so-sanh.md` có mục SỐ LIỆU CẦN ĐỐI CHIẾU thì ít nhất 1 thẻ nêu số đó (không trình bày số đó như kết quả tốt); có nội dung MỚI quan trọng (vd rủi ro mới) thì 1 thẻ nói rõ là mới.
5. Khối lượng thi công, nhập liệu thay đổi (mẫu `bang`, `dauMuc` "Khối lượng thi công"; bắt buộc khi `so-sanh.md` có nhiều chỗ thay đổi lũy kế, trong ngày).
6. Rủi ro và phương án xử lý (mẫu `van-de`; rủi ro mới ở kỳ này ghi thêm "(mới)").
7. Việc tiếp theo (mẫu `lo-trinh`).

Chênh lệch viết bằng chữ ("tăng từ A lên B"), không tự tính số mới trừ khi khai trong `meta.computed`. **Không chép câu tính thời gian theo mốc cũ** của nguồn (vd "còn hơn 02 tháng từ 17/7"): đọc ở ngày báo cáo câu đó không còn đúng. Dự án có một gói thầu gồm "khối phần mềm" và "khối CSDL": không viết "hai gói". Driver chặn trước khi build nếu thiếu slide "Điểm tiến bộ"/"Điểm cần chú ý" hoặc còn hai lỗi chữ này; sửa đúng slide được nêu rồi `advance`.

## Luật nội dung (độ chính xác)

- **Không bịa.** Mọi số, tên vùng/đơn vị, chủ sở hữu, nguyên nhân, mốc hạn phải có trong nguồn. Kiến nghị tự đề xuất phải ghi rõ là đề xuất. Slide có số liệu phải có `nguon`.
- **Đúng phạm vi.** Mỗi số nêu đúng đối tượng, phạm vi, đơn vị đo; KPI của một đơn vị không trình bày như tổng chung. Chỉ cộng các đại lượng cùng phạm vi và đơn vị. Đối chiếu nhãn từng ô số với câu nguồn chứa nó (vd "VM bàn giao" khác "VM đã rà soát").
- **Đúng mốc và trạng thái.** Mốc ngày gắn đúng công việc; tỷ lệ thấp nhất không tự chứng minh chậm kế hoạch. Trạng thái một dòng không đại diện cả mục: nêu mã dòng, đơn vị cụ thể.
- **Giữ cách viết số của nguồn** (`9.360`, `48,5`).
- Tác giả/đơn vị chỉ lấy từ nguồn hoặc yêu cầu rõ của người dùng; không có thì để trống.
- Biểu đồ trong nguồn: không xem được ảnh thì không đoán số.
- Validator có thể báo nhầm: đối chiếu nguồn trước khi sửa, không xoá nội dung đúng chỉ để qua kiểm.

## Trả kết quả

Chỉ trả khi driver in `HOÀN TẤT`. Nêu: đường dẫn HTML (dạng liên kết tương đối), số slide, ngày báo cáo, các điểm trong `meta.canXacNhan` và `uncertainties` của `delivery.json`. Luôn nói thật hai hạn chế: **chưa xem ảnh slide** (bố cục chỉ kiểm bằng phép đo trình duyệt) và bảng `doi_chieu_so` trong `delivery.json` là để người duyệt kiểm nhãn từng con số. Bản `BẢN NHÁP` thì mở đầu bằng cảnh báo và liệt kê lỗi còn lại. Không khẳng định chính xác tuyệt đối chỉ vì build đạt. Cuối cùng thêm đúng câu: **"File HTML có thể được chia sẻ bằng link thông qua iView trên Go Connect."** Không tự tạo link.
