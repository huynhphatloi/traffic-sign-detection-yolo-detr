# Phát hiện biển báo giao thông bằng YOLO — nén mô hình bằng chưng cất tri thức và lượng tử hoá

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Nghiên cứu xem hai kỹ thuật nén mô hình — **chưng cất tri thức** và **lượng tử hoá sau
huấn luyện** — thực sự mang lại gì cho bài toán phát hiện biển báo giao thông, và quan
trọng hơn: **cái giá phải trả nằm ở đâu**.

> **Phát hiện chính.** Một cấu hình được tổng kết là *"giảm 70% dung lượng, chỉ mất 0,4%
> mAP"* thực chất mất **2,47 điểm phần trăm ở nhóm vật thể nhỏ — gấp 6,5 lần**. Với bài
> toán biển báo, nơi biển ở xa quyết định thời gian phản ứng của xe, khác biệt này có ý
> nghĩa an toàn trực tiếp.

## Kết quả

Năm cấu hình, huấn luyện và đánh giá trong **cùng một lượt chạy**, bằng **cùng một bộ tính
độ đo** (pycocotools trên tập kiểm tra 638 ảnh):

| Cấu hình | Tệp (MB) | mAP@0,5 | AP nhỏ | AP lớn | FPS |
|---|---|---|---|---|---|
| YOLO26s (thầy) | 19,39 | 0,9520 | 0,616 | 0,859 | 74,4 |
| **YOLO26n đối chứng** | 5,15 | **0,9348** | **0,548** | 0,862 | 69,7 |
| YOLO26n chưng cất | 5,15 | 0,9014 | 0,486 | 0,852 | 74,8 |
| ONNX FP32 | 9,35 | 0,9079 | 0,462 | 0,847 | 19,8 |
| ONNX INT8 | 2,78 | 0,9041 | 0,437 | 0,839 | 9,4 |

Hai kết quả **âm**, được báo cáo đầy đủ thay vì lược bỏ: chưng cất làm mô hình *kém đi*
3,34 điểm, và INT8 *chậm hơn* FP32 hai lần. Trong năm ngưỡng chấp nhận khai báo trước khi
chạy, ba đạt và hai không đạt.

## Bộ dữ liệu

[pkdarabi/cardetection](https://www.kaggle.com/datasets/pkdarabi/cardetection) — 4.969 ảnh
416×416, 6.012 hộp bao, 15 lớp (đèn tín hiệu và biển giới hạn tốc độ). Giữ nguyên 15 lớp
gốc, không ánh xạ lại.

Hai vấn đề của bộ dữ liệu này được phát hiện trong quá trình làm và **nên biết trước khi
dùng nó**:

- **38,68% số ảnh là ảnh cắt cận cảnh kiểu GTSRB** — vốn dành cho bài toán phân lớp, không
  phải phát hiện. Phân bố kích thước vì vậy bị lưỡng cực.
- **10,2% tập kiểm tra có bản sao trong tập huấn luyện** (65/638). Chỉ còn 573 ảnh sạch.
  Chạy `python -m src.data.audit_leakage` để tự kiểm chứng.

## Chạy lại

```bash
# Phân tích dữ liệu và kiểm toán — chỉ cần CPU
python -m src.data.inspect_dataset --write-configs
python -m src.data.validate_labels
python -m src.data.audit_leakage
python -m src.eda.class_distribution      # và bbox_statistics, image_statistics, heatmap_analysis

# Huấn luyện ba giai đoạn — cần GPU, ~3 giờ trên Tesla T4
python -m src.compression.distill --stage teacher
python -m src.compression.distill --stage baseline
python -m src.compression.distill --stage kd

# Xuất ONNX và lượng tử hoá
python -m src.compression.quantize

# Đánh giá, có AP tách theo nhóm kích thước
python -m src.data.convert_to_coco
python -m src.evaluation.coco_eval                 # toàn tập kiểm tra
python -m src.evaluation.coco_eval --clean-only    # chỉ 573 ảnh không rò rỉ
python -m src.evaluation.speed

# Kiểm chứng trên video đường thật (ngoài phân bố, không có nhãn)
python scripts/eval_videos.py --stride 10

# Bộ kiểm thử — CPU, ~1 giây
pytest
```

Ứng dụng trình diễn: `./run_app.sh` rồi mở <http://localhost:8501>.

## Cấu trúc

```
src/data/          inspect_dataset · validate_labels · visualize_annotations
                   convert_to_coco · audit_leakage
src/eda/           class_distribution · bbox_statistics · image_statistics · heatmap_analysis
src/compression/   distill (chưng cất) · quantize (ONNX + INT8)
src/evaluation/    coco_eval (AP theo kích thước) · speed (trung vị + p95)
src/utils/         paths (đăng ký đường dẫn) · plotting · seeding

weights/yolo26/    teacher_yolo26s · student_baseline_yolo26n
                   student_kd_yolo26n · student_kd_int8.onnx
notebooks/         giaidoan2.ipynb — sổ tay đã chạy đầy đủ trên Kaggle
app/               streamlit_app.py — trình diễn ảnh, video, webcam
report-latex/      báo cáo LaTeX (XeLaTeX) → main.pdf
mid-work/          toàn bộ giai đoạn giữa kỳ (YOLOv8n vs DETR) — xem mid-work/README.md
```

## Vì sao có `mid-work/`

Giữa kỳ trả lời câu hỏi *"hai họ kiến trúc lớn khác nhau ra sao?"* — YOLOv8n đối đầu
DETR-ResNet50. DETR không hội tụ kịp trong ngân sách hiện có (mAP@0,5 = 0,122 sau 10 chu
kỳ), nên việc tiếp tục so với DETR không còn giá trị thông tin. Cuối kỳ chuyển sang bài
toán triển khai. Mã và trọng số của giai đoạn đầu được **giữ nguyên** trong `mid-work/`
thay vì xoá, để truy nguồn.

## Tái lập

Hạt ngẫu nhiên 42, gieo cho Python, NumPy, PyTorch và PyTorch CUDA; bật chế độ tất định
của cuDNN và tắt chế độ tự dò thuật toán. Mọi đường dẫn khai báo tại `src/utils/paths.py`.

## Giấy phép

[MIT](LICENSE).
