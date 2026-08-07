# mid-work — công việc giai đoạn giữa kỳ

Thư mục này lưu trữ toàn bộ phần **giữa kỳ** của đề tài. Nội dung ở đây **không còn**
được dùng bởi báo cáo cuối kỳ, nhưng được giữ lại nguyên vẹn để truy nguồn.

## Vì sao tách ra

Giữa kỳ trả lời câu hỏi *"hai họ kiến trúc lớn khác nhau ra sao?"* — YOLOv8n đối đầu
DETR-ResNet50. Kết quả cho thấy DETR không hội tụ kịp trong ngân sách hiện có
(mAP@0,5 = 0,122 sau 10 chu kỳ), nên việc tiếp tục so với DETR không còn giá trị
thông tin.

Cuối kỳ chuyển sang câu hỏi triển khai — *"làm sao đưa mô hình xuống phần cứng hạn
chế?"* — với YOLO26s dạy YOLO26n rồi lượng tử hoá. Toàn bộ mã và trọng số của giai
đoạn đó nằm ở thư mục gốc của dự án.

## Nội dung

```
src/training/       train_yolo.py (YOLOv8n)  ·  train_detr.py (DETR-ResNet50)
src/evaluation/     evaluate_yolo.py · evaluate_detr.py · compare_models.py · benchmark_fps.py
scripts/            build_slides.py (slide giữa kỳ) · patch_notebook*.py
                    run_local_pipeline.py · log_training.py
notebooks/          traffic_sign_detection_pipeline.ipynb  — pipeline giữa kỳ đầy đủ
weights/            yolov8n.pt (tiền huấn luyện COCO)
                    yolov8n_baseline/  — best.pt sau 30 chu kỳ trên bộ biển báo
results/metrics/    yolo_baseline.json · detr_baseline.json
```

## Cách chạy lại nếu cần

Mã ở đây import theo đường dẫn `src.*` của thư mục gốc. Muốn chạy lại, copy ngược tệp
cần dùng về đúng vị trí cũ trong `src/` rồi gọi như bình thường, ví dụ:

```bash
cp mid-work/src/training/train_yolo.py src/training/
python -m src.training.train_yolo --model mid-work/weights/yolov8n.pt --epochs 30
```

Lưu ý `src/training/` đã bị gỡ khỏi cây thư mục chính, cần tạo lại kèm `__init__.py`.

## Những gì KHÔNG nằm ở đây

Phần phân tích dữ liệu (`src/data/`, `src/eda/`) được giữ lại ở thư mục gốc vì nó
không phụ thuộc vào mô hình nào, và báo cáo cuối kỳ vẫn dùng trực tiếp.
