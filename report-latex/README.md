# Khung LaTeX tiểu luận / báo cáo học phần — tiếng Việt

Khung tái sử dụng, rút ra từ đề tài `Latex_Automatic_Grading` đã nộp và chấm đạt.
Giữ **nguyên định dạng** đó (cỡ chữ, lề, kiểu chương mục, trang bìa), chỉ khác một điểm:
**mọi thông tin đề tài gom về một tệp duy nhất** nên dùng lại rất nhanh.

## Bắt đầu một đề tài mới trong 5 phút

1. **Copy cả thư mục này**, đổi tên theo đề tài mới.
2. Mở `config/metadata.tex` → sửa tên đề tài, học viên, học phần, GVHD, ngày tháng.
   *Đây là tệp duy nhất bắt buộc phải sửa.* Trang bìa 1, bìa lót, lời cam đoan, lời cảm ơn và
   metadata PDF đều tự lấy thông tin từ đây.
3. Thay `logo.png` bằng logo trường (nếu khác).
4. Viết nội dung trong `chapters/`.
5. Thêm tài liệu tham khảo vào `references.bib`.

## Biên dịch

**Bắt buộc dùng XeLaTeX** (vì dùng `fontspec` + `polyglossia`).

- **Overleaf:** upload cả thư mục → Menu → Compiler → **XeLaTeX** → Recompile.
- **Máy cá nhân:**

```bash
latexmk -xelatex -shell-escape main.tex
# hoặc thủ công (chạy đủ 4 lượt để mục lục + trích dẫn đúng):
xelatex main && bibtex main && xelatex main && xelatex main
```

## Cấu trúc thư mục

```
├── main.tex                      preamble + thứ tự các phần (ít khi phải sửa)
├── config/
│   └── metadata.tex              ★ SỬA DUY NHẤT TỆP NÀY cho mỗi đề tài mới
├── frontmatter/
│   ├── cover1.tex                trang bìa (có khung chấm điểm)
│   ├── cover2.tex                trang bìa lót (có logo)
│   ├── loi_cam_doan.tex
│   ├── loi_cam_on.tex
│   ├── tom_tat.tex
│   ├── danh_muc_tu_viet_tat.tex
│   └── danh_muc_hinh_bang.tex
├── chapters/
│   ├── 01_gioi_thieu.tex
│   ├── 02_co_so_ly_thuyet.tex
│   ├── 03_phuong_phap.tex
│   ├── 04_ket_qua.tex
│   └── 05_tong_ket.tex
├── appendices/
│   └── appendix_resources.tex
├── figures/                      ảnh; đặt chữ ký tại figures/chuky.png
├── references.bib
├── SNIPPETS.md                   ★ sổ tay copy/paste bảng, hình, công thức...
└── README.md
```

## Định dạng đã cài sẵn (theo quy định trường)

| Mục | Giá trị |
|---|---|
| Lớp tài liệu | `extreport`, cỡ chữ **13pt** |
| Phông chữ | Times New Roman (tự lùi về TeX Gyre Termes nếu máy không có) |
| Lề | trên 3cm · dưới 3cm · trái 3cm · phải 2cm |
| Giãn dòng | 1,5 |
| Thụt đầu dòng | 1,25cm |
| Số trang | giữa **đầu trang**, không kẻ đường |
| Tên chương | `CHƯƠNG n : TÊN CHƯƠNG IN HOA`, cỡ `\LARGE` đậm |
| Mục / tiểu mục | 16pt / 15pt đậm |
| Đánh số hình, bảng, công thức | theo chương (Hình 3.1, Bảng 3.2...) |
| Trích dẫn | IEEEtran — `[1]`, `[2]`... |

## Quy ước viết cho nhất quán

- **Tham chiếu chéo:** `Bảng~\ref{tab:...}`, `Hình~\ref{fig:...}`, `Chương~\ref{ch:...}`.
  Luôn dùng dấu `~` để không bị ngắt dòng giữa chữ và số.
- **Nhãn:** `ch:` chương · `sec:` mục · `tab:` bảng · `fig:` hình · `eq:` công thức ·
  `alg:` thuật toán · `lst:` mã nguồn · `app:` phụ lục.
- **Chú thích bảng đặt TRÊN bảng, chú thích hình đặt DƯỚI hình.**
- **Số thập phân kiểu Việt Nam:** `0,8429`; phân cách hàng nghìn bằng dấu chấm: `39.209`.
- **Gạch ngang dài** trong câu: gõ `---`.

Xem `SNIPPETS.md` để copy/paste nhanh mọi cú pháp thường dùng.

## Bật chữ ký trong lời cam đoan

1. Đặt ảnh chữ ký (nền trong suốt, PNG) tại `figures/chuky.png`.
2. Trong `config/metadata.tex`, đổi `\showsignaturefalse` → `\showsignaturetrue`.

Nếu không bật, phần chữ ký để trống một khoảng để ký tay sau khi in.

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân & cách xử lý |
|---|---|
| `Package fontspec Error: The font "Times New Roman" cannot be found` | Máy không cài Times New Roman. Khung này đã tự lùi về TeX Gyre Termes (cùng kích thước chữ) nên thường không gặp; nếu vẫn lỗi, kiểm tra đã chọn **XeLaTeX** chưa. |
| Chữ tiếng Việt mất dấu hoặc thành ô vuông | Đang biên dịch bằng pdfLaTeX. Chuyển sang **XeLaTeX**. |
| `I found no \bibstyle command` | Chưa chạy BibTeX, hoặc chạy sai thứ tự. Chạy đủ: xelatex → bibtex → xelatex → xelatex. |
| Mục lục / số hình bị sai hoặc hiện `??` | Chưa biên dịch đủ số lượt. Biên dịch lại lần nữa. |
| `Undefined control sequence \projecttitle` | Thiếu dòng `\input{config/metadata}` trong `main.tex`. |
| Bảng tràn ra ngoài lề | Dùng `\small` hoặc `\footnotesize`, hoặc chuyển sang `tabularx` với cột `X`. |
| Hình nhảy sang trang khác | Đã dùng `[H]` (bắt buộc đúng vị trí) — cần gói `float`, đã có sẵn. |
