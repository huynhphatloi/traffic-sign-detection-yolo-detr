# Midterm Presentation Outline (24 slides)

Robust and Data-Efficient Traffic Sign Detection for Self-Driving Cars using YOLO and DETR.
Each slide notes the artifact to drop in.

1. **Title** — project title + course/date.
2. **Team** — Loi (lead/data/YOLO), Vinh (EDA), Tu (data quality/DETR).
3. **Problem motivation** — perception for self-driving cars; reading signs is safety-critical.
4. **Why traffic-sign detection matters** — speed limits, stop, lights → vehicle behavior.
5. **Research question** — robust + data-efficient detection with YOLO and DETR.
6. **Two-phase roadmap** — Phase 1 analysis+baselines → Phase 2 improvement+deployment.
7. **Main dataset** — pkdarabi/cardetection, *Traffic Signs Detection* (sign detection, not cars).
8. **Dataset structure** — train/valid/test, images/+labels/ (`dataset_summary.csv`).
9. **Annotation format** — detected YOLO TXT + 15 classes (`configs/classes.yaml`).
10. **Dataset examples** — annotated samples (`results/samples/annotated_train_samples/`).
11. **Class distribution** — `results/eda/class_distribution.png` (imbalance: Speed-Limit-heavy).
12. **Bounding-box statistics** — `bbox_area.png`, `bbox_wh.png`, `bbox_aspect_ratio.png`.
13. **Small-object analysis** — `bbox_size_categories.png` (small = <1% area).
14. **Object location heatmap** — `object_center_heatmap.png`.
15. **Data quality issues** — `data_quality_report.csv` summary (missing/empty/invalid/corrupt/dups).
16. **Difficult sample examples** — smallest/blurry/low-light gallery (`03_data_quality.ipynb`).
17. **YOLO baseline setup** — YOLOv8n, imgsz 640, 30 epochs, flip-LR off.
18. **DETR baseline setup** — detr-resnet-50, batch 2, ~10 epochs, COCO format.
19. **Initial YOLO vs DETR comparison** — `comparison.csv` table (mAP, P, R, FPS).
20. **Robustness & data-efficiency plan** — low-light/blur/noise/resolution + 10/25/50/100% labels.
21. **Phase 2 application plan** — Gradio demo (image/video/webcam, FPS, confidence slider).
22. **Hugging Face & Gradio deployment plan** — model on HF Hub, demo on HF Spaces.
23. **Team responsibilities** — per-member Phase 1/2 ownership.
24. **Midterm conclusion** — "dataset understood + validated, challenges identified, baselines trained."
