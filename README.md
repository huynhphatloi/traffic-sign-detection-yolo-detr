# Traffic Signs Detection for Self-Driving Cars: YOLO vs DETR

A comparative study of **YOLO** (convolutional) and **DETR** (transformer) for traffic-sign
object detection on the **[pkdarabi/cardetection](https://www.kaggle.com/datasets/pkdarabi/cardetection/data)**
("Traffic Signs Detection") dataset, with a real-time detection app and a robustness analysis
under simulated driving conditions.

> **Research question:** How do YOLO and DETR compare for traffic-sign detection in self-driving
> scenarios in terms of detection accuracy, inference speed, robustness, and real-time deployment
> suitability?

Single dataset, **native 15 classes** (Red/Green Light, Stop, Speed Limit 10–120). No
multi-dataset mixing — see *Future work*.

---

## Team

| Member | Role | Owns |
|--------|------|------|
| **Loi** | Team lead | Data pipeline · EDA · evaluation & comparison · app integration · `notebooks/00`, `01`, `04` |
| **Vinh** | YOLO track | YOLO training/tuning/eval · backend inference · real-time optimization · `notebooks/02`, `05`, `06` |
| **Tu** | DETR track | DETR training/tuning/eval · robustness analysis · error analysis · app UI · `notebooks/03`, `07`, `08` |

**Full per-member task breakdown, dependencies, and milestones: see [TEAM.md](TEAM.md).**

---

## Deliverables

### Midterm — Dataset Analysis Report (`notebooks/01_eda`)
Presentation + written report covering:
- Dataset description (scale, source, format)
- Class distribution and imbalance (most boxes are Speed Limits)
- Bounding-box size statistics (small-object challenge)
- Objects-per-image and sign-location heatmap
- Data quality notes (occlusion, blur, label issues)
- Preprocessing and augmentation plan
- Planned YOLO-vs-DETR methodology for the final project

**Owner: Loi** (runs `01_eda.ipynb`, writes the report, all three present)

### Final — Working Application + Report
Full model training, comparison, and the deployed real-time app:
- YOLO baseline + ablations (Vinh)
- DETR baseline (Tu)
- Accuracy vs speed comparison table + chart (Loi)
- Augmentation ablation and limited-data study (Vinh)
- Robustness analysis under simulated driving conditions (Tu)
- Error analysis and per-class AP breakdown (Tu)
- Real-time Streamlit demo video (all three)

---

## What's in here
| Area | Module(s) |
| ---- | --------- |
| Data prep | `src/data/prepare_dataset.py` (Roboflow → Ultralytics + verify), `convert_to_coco.py` (DETR), `degrade.py` (robustness conditions), `visualize_annotations.py` |
| Training | `src/training/train_yolo.py` (`--aug`, `--fraction`), `train_detr.py` |
| Evaluation | `evaluate_yolo.py`, `evaluate_detr.py`, `benchmark_fps.py`, `robustness_eval.py`, `compare_models.py` |
| EDA / viz | `src/visualization/` (class balance, box stats, heatmap, predictions, error gallery) |
| App | `src/app/app.py` (Streamlit real-time demo + warning panel) |
| Notebooks | `notebooks/00`–`08` — thin orchestration over the `src` modules |

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Training needs a GPU — do the heavy work on Colab (`notebooks/00_colab_setup.ipynb`) and keep your
local machine for the EDA and the webcam demo.

## Workflow
```bash
# 1. Get the dataset (Kaggle API) and build it
kaggle datasets download -d pkdarabi/cardetection -p data/raw/cardetection --unzip
python -m src.data.prepare_dataset --write-configs   # normalize layout + sync configs from data.yaml
python -m src.data.convert_to_coco                   # COCO JSON for DETR
python -m src.data.visualize_annotations --yolo-root data/processed/yolo/cardetection --split val

# 2. EDA (midterm core)
python -m src.visualization.plot_eda --yolo-root data/processed/yolo/cardetection --name cardetection

# 3. Train baselines
python -m src.training.train_yolo --data configs/cardetection.yaml --name yolo_baseline
python -m src.training.train_detr --coco data/processed/coco --split cardetection --name detr_baseline

# 4. Evaluate + compare
python -m src.evaluation.evaluate_yolo --weights weights/yolo/yolo_baseline/best.pt --data configs/cardetection.yaml --tag yolo_baseline
python -m src.evaluation.evaluate_detr --model weights/detr/detr_baseline --coco data/processed/coco --split cardetection --tag detr_baseline
python -m src.evaluation.benchmark_fps --weights weights/yolo/yolo_baseline/best.pt
python -m src.evaluation.compare_models --metrics-dir results/metrics --out results/plots

# 5. Ablations
python -m src.training.train_yolo --data configs/cardetection.yaml --aug strong   --name yolo_aug_strong
python -m src.training.train_yolo --data configs/cardetection.yaml --fraction 0.25 --name yolo_25pct

# 6. Robustness (simulate driving conditions, then re-evaluate)
python -m src.data.degrade --split test --conditions lowlight,motionblur,noise,smallsigns --severity 0.5
python -m src.evaluation.robustness_eval --weights weights/yolo/yolo_baseline/best.pt \
    --clean-root data/processed/yolo/cardetection --degraded-root data/degraded --tag yolo_baseline

# 7. Error analysis
python -m src.visualization.error_gallery --weights weights/yolo/yolo_baseline/best.pt \
    --yolo-root data/processed/yolo/cardetection --split test --n 20
```

## Real-time app
```bash
streamlit run src/app/app.py
```
Webcam / uploaded video; shows boxes, labels, confidence, live FPS, per-class counts, a
driving-style **warning panel**, screenshot and annotated-video save.

## Notebooks
`00_colab_setup` → `01_eda` → `02_yolo_baseline` → `03_detr_baseline` → `04_comparison` →
`05_augmentation_ablation` → `06_limited_data` → `07_robustness` → `08_error_analysis`.
Each (except 00) starts with a setup cell that locates the project root in Colab or locally.

## Report structure
**Midterm — dataset analysis:** description, annotation format, class distribution/imbalance,
bounding-box statistics, small-object analysis, data-quality notes, preprocessing + augmentation
plan, and the planned YOLO-vs-DETR methodology (`notebooks/01_eda`).

**Final — models + app:** YOLO training, DETR training, accuracy comparison, speed comparison,
augmentation ablation, limited-data study, robustness analysis, error analysis, the real-time app,
and a demo video.

## Execution priority
| Priority | Task |
| -------- | ---- |
| P0 | Download dataset · `prepare_dataset` (YOLO) · `convert_to_coco` (DETR) · YOLO + DETR baselines |
| P1 | Evaluate mAP/FPS/size · build real-time app · error analysis |
| P2 | Augmentation ablation · limited-data study |
| P3 | Robustness degradation tests |

## Future work
Extend to full road-scene perception (vehicles, pedestrians, traffic lights, lane markings) and to
other regions' signs (e.g. Vietnamese). Out of scope here to keep the project clean: traffic signs only.
# traffic-sign-detection-yolo-detr
