# Traffic Sign Detection for Self-Driving Cars: YOLO vs DETR

Robust and data-efficient **traffic-sign object detection** comparing **YOLO** (one-stage CNN) and
**DETR** (transformer) on the teacher-provided Kaggle dataset
**[pkdarabi/cardetection](https://www.kaggle.com/datasets/pkdarabi/cardetection/data)**
(*Traffic Signs Detection*). Despite the URL name, the task is **traffic-sign** detection, not car
detection. **15 native classes** (Green/Red Light, Speed Limit 10–120, Stop) — kept as-is, no remapping.

> **Research question:** How can traffic-sign detection for self-driving car scenarios be made more
> **robust** and **data-efficient** using YOLO and DETR?

**Team:** Loi (lead · data pipeline · YOLO · integration) · Vinh (EDA · data mining) · Tu (data
quality · DETR · robustness plan).

---

## Status

**Phase 1 (Midterm) — in progress.** Dataset inspection, validation, EDA, YOLO + DETR baselines, and
the initial comparison, plus the midterm report and slides.

**Phase 2 (Final) — planned.** Model improvement, robustness + data-efficiency experiments, error
analysis, a **Gradio** app, and **Hugging Face Hub + Spaces** deployment. (`app/` and `huggingface/`
are placeholders until then.)

## Repository layout

```
configs/        data.yaml (Ultralytics) + classes.yaml (15 classes, auto-synced from the dataset)
notebooks/      00 setup · 01 inspection · 02 EDA · 03 data quality · 04 YOLO · 05 DETR · 06 comparison
src/data/       inspect_dataset · validate_labels · visualize_annotations · convert_to_coco
src/eda/        class_distribution · bbox_statistics · image_statistics · heatmap_analysis
src/training/   train_yolo · train_detr
src/evaluation/ evaluate_yolo · evaluate_detr · benchmark_fps · compare_models
src/utils/      paths (central path registry) · plotting
results/        eda/ samples/ tables/ metrics/ plots/   (generated; gitignored)
reports/        midterm_report.md            slides/  midterm_presentation_outline.md
app/ huggingface/   Phase 2 placeholders
```

Notebooks are **thin orchestration** over `src/`; every script is also runnable as
`python -m src.<pkg>.<module>`.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Training needs a GPU** — run the training notebooks on **Colab** (`notebooks/00_colab_setup.ipynb`).
Inspection, validation, and EDA run fine on a laptop (CPU).

## Workflow

```bash
# 1. Get the dataset (Kaggle API) into data/raw, then place the Roboflow export at
#    data/processed/cardetection/{train,valid,test}/{images,labels}
kaggle datasets download -d pkdarabi/cardetection -p data/raw --unzip

# 2. Inspect + sync configs (writes results/tables/dataset_summary.csv, regenerates classes.yaml)
python -m src.data.inspect_dataset --write-configs

# 3. Validate annotations (writes results/tables/data_quality_report.csv)
python -m src.data.validate_labels

# 4. Annotated samples (required before training)
python -m src.data.visualize_annotations --split train --n 12

# 5. EDA (writes results/eda/*.png + results/tables/*.csv)
python -m src.eda.class_distribution
python -m src.eda.bbox_statistics
python -m src.eda.image_statistics
python -m src.eda.heatmap_analysis

# 6. Baselines (GPU / Colab)
python -m src.training.train_yolo --epochs 30 --name yolo_baseline
python -m src.evaluation.evaluate_yolo --weights weights/yolo/yolo_baseline/best.pt --split test

python -m src.data.convert_to_coco
python -m src.training.train_detr --epochs 10 --batch 2 --name detr_baseline
python -m src.evaluation.evaluate_detr --model-dir weights/detr/detr_baseline --split test

# 7. Initial comparison
python -m src.evaluation.compare_models
```

## Data & weights policy

`data/`, `weights/`, and heavy `results/` outputs are **gitignored** — keep them on Google Drive.
Only code, notebooks, configs, small tables, the report, and slides are committed.

## Future work

Optional Phase 2 extension: Vietnamese street traffic-sign images/video for real-world testing. The
teacher dataset stays the **main required dataset** — not replaced.
