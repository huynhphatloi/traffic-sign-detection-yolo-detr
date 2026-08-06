# Sổ tay cú pháp — copy/paste nhanh

Tất cả đoạn dưới đây đã khớp với định dạng trong `main.tex`. Copy thẳng vào chương.

---

## Bảng cơ bản (booktabs)

```latex
\begin{table}[H]
\centering
\caption{Chú thích bảng đặt PHÍA TRÊN bảng}
\label{tab:ten_nhan}
\small
\begin{tabular}{lrr}
\toprule
\textbf{Cột 1} & \textbf{Cột 2} & \textbf{Cột 3} \\
\midrule
Hàng 1 & 0,8429 & 1.234 \\
Hàng 2 & 0,8514 & 5.678 \\
\bottomrule
\end{tabular}
\end{table}
```

Tham chiếu: `Bảng~\ref{tab:ten_nhan}` — **luôn dùng `~`** để không bị ngắt dòng giữa "Bảng" và số.

---

## Bảng dài nhiều trang (longtable)

```latex
\begin{longtable}{@{}rlrr@{}}
\caption{Chú thích bảng dài}
\label{tab:bang_dai}\\
\toprule
\textbf{ID} & \textbf{Tên} & \textbf{Giá trị} & \textbf{Ghi chú} \\
\midrule
\endfirsthead

\multicolumn{4}{@{}l}{\itshape (tiếp theo trang trước)}\\
\toprule
\textbf{ID} & \textbf{Tên} & \textbf{Giá trị} & \textbf{Ghi chú} \\
\midrule
\endhead

\bottomrule
\endfoot

1 & Mục thứ nhất & 0,1234 & --- \\
2 & Mục thứ hai  & 0,5678 & --- \\
\end{longtable}
```

---

## Bảng có cột tự co giãn (tabularx)

```latex
\begin{table}[H]
\centering
\caption{Bảng có cột mô tả dài}
\label{tab:tabularx}
\small
\begin{tabularx}{\textwidth}{lX}
\toprule
\textbf{Thuật ngữ} & \textbf{Giải thích} \\
\midrule
Thuật ngữ A & Phần mô tả dài sẽ tự động xuống dòng vừa khít chiều rộng trang. \\
\bottomrule
\end{tabularx}
\end{table}
```

---

## Hình một ảnh

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{figures/ten_hinh.png}
\caption{Chú thích hình đặt PHÍA DƯỚI hình}
\label{fig:ten_nhan}
\end{figure}
```

## Hình hai ảnh cạnh nhau

```latex
\begin{figure}[H]
\centering
\begin{subfigure}[b]{0.48\textwidth}
  \centering
  \includegraphics[width=\textwidth]{figures/hinh_a.png}
  \caption{Chú thích ảnh trái}
  \label{fig:hinh_a}
\end{subfigure}
\hfill
\begin{subfigure}[b]{0.48\textwidth}
  \centering
  \includegraphics[width=\textwidth]{figures/hinh_b.png}
  \caption{Chú thích ảnh phải}
  \label{fig:hinh_b}
\end{subfigure}
\caption{Chú thích chung cho cả hai ảnh}
\label{fig:hinh_ghep}
\end{figure}
```

---

## Công thức

```latex
% Công thức có đánh số (tham chiếu bằng \eqref)
\begin{equation}
\label{eq:ten_nhan}
\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N} y_i \log \hat{y}_i
\end{equation}

% Nhiều dòng căn theo dấu =
\begin{align}
a &= b + c \\
  &= d + e
\end{align}

% Công thức trong dòng: $x^2 + y^2 = z^2$
```

---

## Danh sách

```latex
\begin{itemize}[leftmargin=1.5cm]
\item Mục thứ nhất.
\item Mục thứ hai.
\end{itemize}

\begin{enumerate}[leftmargin=1.5cm]
\item Mục đánh số thứ nhất.
\item Mục đánh số thứ hai.
\end{enumerate}

% Danh sách có nhãn tự đặt
\begin{description}[leftmargin=1.5cm]
\item[Thuật ngữ A] giải thích.
\item[Thuật ngữ B] giải thích.
\end{description}
```

---

## Mã nguồn

```latex
\begin{lstlisting}[language=Python,caption={Chú thích đoạn mã},label={lst:ten_nhan}]
def ham_mau(x):
    return x ** 2
\end{lstlisting}
```

> **Lưu ý:** phần `caption` của `lstlisting` **không nên có dấu tiếng Việt phức tạp** nếu gặp lỗi
> font; khi đó viết chú thích bằng đoạn văn ngay trên khối mã.

---

## Thuật toán

```latex
\begin{algorithm}[H]
\caption{Tên thuật toán}
\label{alg:ten_nhan}
\begin{algorithmic}[1]
\State \textbf{Đầu vào:} $D$, $\theta$
\State \textbf{Đầu ra:} $M$
\For{$t = 1 \dots T$}
    \State Cập nhật tham số
    \If{hội tụ}
        \State \textbf{break}
    \EndIf
\EndFor
\State \Return $M$
\end{algorithmic}
\end{algorithm}
```

---

## Hộp nhấn mạnh (macro riêng của khung này)

```latex
\hopnhanmanh{Nội dung nhận xét quan trọng.}

% Đổi nhãn mặc định "Nhận xét":
\hopnhanmanh[Phát hiện chính]{Nội dung phát hiện.}
```

---

## Trích dẫn

```latex
\cite{khoa_bibtex}                  % [1]
\cite{khoa1,khoa2}                  % [1], [2]
```

Thêm mục vào `references.bib`:

```bibtex
@article{khoa_bibtex,
  title   = {Tên bài báo},
  author  = {Nguyen, Van A and Tran, Thi B},
  journal = {Tên tạp chí},
  volume  = {32},
  pages   = {323--332},
  year    = {2024}
}
```

---

## Tham chiếu chéo — quy ước thống nhất

| Loại | Cú pháp | Hiển thị |
|---|---|---|
| Chương | `Chương~\ref{ch:...}` | Chương 3 |
| Mục | `Mục~\ref{sec:...}` | Mục 3.2 |
| Bảng | `Bảng~\ref{tab:...}` | Bảng 3.1 |
| Hình | `Hình~\ref{fig:...}` | Hình 3.1 |
| Công thức | `Công thức~\eqref{eq:...}` | Công thức (3.1) |
| Thuật toán | `Thuật toán~\ref{alg:...}` | Thuật toán 3.1 |
| Phụ lục | `Phụ lục~\ref{app:...}` | Phụ lục A |

**Quy ước đặt nhãn:** `ch:` chương · `sec:` mục · `tab:` bảng · `fig:` hình · `eq:` công thức ·
`alg:` thuật toán · `lst:` mã nguồn · `app:` phụ lục.

---

## Ký tự đặc biệt hay gặp

| Muốn hiện | Gõ |
|---|---|
| Gạch ngang dài (—) | `---` |
| Gạch nối trung bình (–) | `--` |
| Dấu ngoặc kép "..." | ` ``...'' ` |
| % | `\%` |
| & | `\&` |
| _ | `\_` |
| # | `\#` |
| $ | `\$` |
| > < trong bảng | `$>$` `$<$` |
| ~ | `\textasciitilde{}` |

**Số thập phân kiểu Việt Nam:** viết trực tiếp `0,8429` (dấu phẩy), phân cách hàng nghìn bằng
dấu chấm `39.209`.
