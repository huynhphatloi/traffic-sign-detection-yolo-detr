# Robust and Data-Efficient Traffic Sign Detection for Self-Driving Cars using YOLO and DETR
## Midterm Report (Phase 1)

**Team:** Loi (lead · data pipeline · YOLO · integration) · Vinh (EDA · data mining) · Tu (data quality · DETR · robustness plan)

> Fill in every `_TBD_` from the generated artifacts: `results/tables/*.csv`, `results/eda/*.png`,
> `results/metrics/*.json`, `results/samples/`. Each section names the file it draws from.

---

## Abstract
_TBD_ — One paragraph: the project (traffic-sign detection for self-driving cars on the
`pkdarabi/cardetection` dataset), Phase 1 work (inspection, validation, EDA, YOLO + DETR baselines,
initial comparison), and the planned Phase 2 (robustness, data-efficiency, Gradio + HF deployment).

## 1. Introduction
- **Background & motivation:** traffic-sign detection is a core perception task for self-driving cars
  and ADAS; missed or misread signs (speed limits, stop, traffic lights) are safety-critical.
- **Problem statement:** detect and classify traffic signs in driving images, robustly and with
  limited labels.
- **Research question:** *How can traffic sign detection for self-driving car scenarios be made more
  robust and data-efficient using YOLO and DETR?*
- **Phases:** Phase 1 = dataset analysis + baselines; Phase 2 = improvement, robustness/data-efficiency,
  deployment.

## 2. Dataset Description
- **URL:** https://www.kaggle.com/datasets/pkdarabi/cardetection/data
- **Title:** Traffic Signs Detection — Signs Detection For Self-Driving Cars (despite the `cardetection`
  URL, the task is **traffic-sign** detection, not car detection).
- **Format:** _TBD_ — from `results/tables/dataset_summary.csv` (`format` column; expected: YOLO TXT,
  Roboflow export with `data.yaml`).
- **Classes (15):** Green Light, Red Light, Speed Limit 10–120, Stop. See `configs/classes.yaml`.
- **Splits & counts:** _TBD_ — images / label files / boxes per `train`/`valid`/`test` from
  `dataset_summary.csv`.

## 3. Data Mining and Exploratory Data Analysis
Source: `results/eda/` + `results/tables/{class_distribution,bbox_size_categories,image_statistics}.csv`.
- **Image & annotation counts:** _TBD_ (`images_per_split.png`).
- **Class distribution & imbalance:** _TBD_ — imbalance ratio (max/min) from `class_distribution.csv`;
  expected: Speed-Limit classes dominate (`class_distribution.png`).
- **Bounding-box size:** _TBD_ — area / w-h / aspect distributions (`bbox_area.png`, `bbox_wh.png`,
  `bbox_aspect_ratio.png`).
- **Small-object analysis:** _TBD_ — small/medium/large split (`bbox_size_categories.png`); small =
  <1% of image area.
- **Objects per image:** _TBD_ (`objects_per_image.png`).
- **Image resolution:** _TBD_ (`image_resolution.png`).
- **Object location:** _TBD_ — center heatmap (`object_center_heatmap.png`); expected concentration
  near the horizon/road sides.

## 4. Data Quality Assessment
Source: `results/tables/data_quality_report.csv` + `03_data_quality.ipynb`.
- Missing labels / empty labels / invalid boxes / out-of-bounds boxes / corrupt images / duplicate
  image names: _TBD_ counts from `summarize()`.
- **Difficult samples:** small, distant, blurry, occluded, low-light signs — gallery in
  `03_data_quality.ipynb`.
- **Limitations:** _TBD_.

## 5. Baseline Deep Learning Experiments
- **YOLO setup:** YOLOv8n, pretrained, imgsz 640, 30 epochs, **flip-LR off** (directional signs).
  (`src/training/train_yolo.py`, `04_yolo_baseline.ipynb`.)
- **DETR setup:** `facebook/detr-resnet-50`, pretrained, batch 2, ~10 epochs, COCO annotations
  (`src/training/train_detr.py`, `05_detr_baseline.ipynb`).
- **Metrics (test split):** _TBD_ from `results/metrics/{yolo,detr}_baseline.json`.

### 5.1 Initial YOLO vs DETR comparison
Source: `results/tables/comparison.csv`.

| Model    | Status               | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | FPS  | Notes                |
| -------- | -------------------- | ------: | -----------: | --------: | -----: | ---: | -------------------- |
| YOLOv8n  | Baseline             |   _TBD_ |        _TBD_ |     _TBD_ |  _TBD_ | _TBD_| Fast one-stage       |
| DETR-R50 | Lightweight baseline |   _TBD_ |        _TBD_ |     _TBD_ |  _TBD_ | _TBD_| Transformer baseline |

## 6. Robustness and Data-Efficiency Plan (Phase 2)
- **Robustness conditions:** low light (darken), motion blur (blur kernel), noise (Gaussian),
  resolution degradation (down/up-scale), small-object difficulty (evaluate small boxes separately).
  Report mAP/recall/confidence drop + qualitative examples.
- **Data-efficiency:** train YOLO on 10% / 25% / 50% / 100% of the labels; DETR on 50% / 100% only
  (slower). Plot performance vs label fraction.

## 7. Planned Phase 2 Methodology
- Improved YOLO (YOLOv8s/m, augmentation ablation) and DETR (longer schedule).
- Full comparison (accuracy vs speed).
- **Gradio** application (image/video/webcam, boxes, confidence slider, FPS).
- **Hugging Face Hub** model upload + **Spaces** demo deployment.

## 8. Team Member Contributions
- **Loi:** repo/data pipeline, annotation validation, YOLO baseline, integration, report assembly.
- **Vinh:** EDA, data mining, statistics tables/plots, initial comparison table.
- **Tu:** data quality, difficult-sample gallery, DETR baseline, literature review, robustness/
  data-efficiency experiment design.

## 9. Expected Challenges
Small/distant signs; class imbalance (Speed-Limit-heavy); annotation quality; DETR training cost;
real-time deployment constraints.

## 10. Conclusion
_TBD_ — summarize Phase 1 findings (dataset understood + validated, baselines trained, initial
comparison) and the Phase 2 plan.

## References
- Redmon et al., *You Only Look Once* (YOLO). Jocher et al., *Ultralytics YOLOv8*.
- Carion et al., *End-to-End Object Detection with Transformers* (DETR), ECCV 2020.
- Dataset: pkdarabi, *Traffic Signs Detection* (Kaggle).
- _TBD_ — add traffic-sign-detection / robustness / data-efficient-learning citations (Tu's review).
