# Team Task Breakdown

3 members: **Loi** (team lead), **Vinh** (YOLO track), **Tu** (DETR track).
Two graded deliverables: **Midterm = dataset analysis report**, **Final = working application from the dataset**.

> **Dependency order (read first):**
> 1. **Loi** must finish data prep (P0) before anyone can train — it produces `data/processed/`.
> 2. **Vinh's** trained YOLO checkpoint (`weights/yolo/yolo_baseline/best.pt`) is needed by **Tu** for robustness + error analysis, and by **Loi** for the app demo.
> 3. **Tu's** DETR work is independent and can run in parallel with Vinh.

---

## Loi — Team Lead · Data Pipeline · EDA · Comparison · Integration

**Owns:** `src/data/{prepare_dataset,convert_to_coco,visualize_annotations,common}.py`,
`src/visualization/plot_eda.py`, `src/evaluation/compare_models.py`, app integration.
**Notebooks:** `00_colab_setup`, `01_eda`, `04_comparison`.

### Midterm tasks (dataset analysis)
1. **Repo setup** — push project to GitHub, make sure Vinh & Tu can clone and run `00_colab_setup` on Colab.
2. **Build the dataset (P0 — unblocks the whole team):**
   ```bash
   kaggle datasets download -d pkdarabi/cardetection -p data/raw/cardetection --unzip
   python -m src.data.prepare_dataset --write-configs
   python -m src.data.convert_to_coco
   python -m src.data.visualize_annotations --yolo-root data/processed/yolo/cardetection --split val
   ```
3. **Run the EDA** (`notebooks/01_eda`): `plot_eda` → class distribution, box-size histograms,
   objects-per-image, sign-location heatmap, small-object summary.
4. **Write the midterm report + slides** — lead author. Pull in Vinh's detection-angle notes and
   Tu's data-quality notes (below). All three present.

### Final tasks (application)
5. **Comparison** (`notebooks/04_comparison`): collect everyone's metrics JSON and run
   `compare_models` → the accuracy-vs-speed table + `accuracy_vs_speed.png` chart. This is the
   headline result of the project.
6. **App integration:** make sure `streamlit run src/app/app.py` loads the best checkpoint, the
   warning panel + FPS work end-to-end. Coordinate the demo video (all three).
7. **Final report assembly:** combine YOLO (Vinh), DETR + robustness + errors (Tu), and the
   comparison into one document; write intro, methodology, and conclusion.

---

## Vinh — YOLO Track · Real-Time Backend

**Owns:** `src/training/train_yolo.py`, `src/evaluation/{evaluate_yolo,benchmark_fps}.py`,
`src/app/inference.py` (YoloDetector + real-time speed).
**Notebooks:** `02_yolo_baseline`, `05_augmentation_ablation`, `06_limited_data`.

### Midterm tasks (support dataset analysis)
1. **Detection-angle EDA notes** for the report: from `plot_eda` output, characterize the
   small-object problem (how many boxes are <1% of image area) and what input size / preprocessing
   YOLO will need. Hand these to Loi.
2. **Document the augmentation plan** in the midterm methodology section: which augmentations
   (brightness, blur, scale, translation, mosaic) and why horizontal flip is OFF (directional signs).
3. *(optional)* run a quick 5-epoch YOLO train to confirm the pipeline works before the report.

### Final tasks (application)
4. **YOLO baseline** (`notebooks/02_yolo_baseline`):
   ```bash
   python -m src.training.train_yolo --data configs/cardetection.yaml --model yolov8s.pt --epochs 100 --name yolo_baseline
   python -m src.evaluation.evaluate_yolo --weights weights/yolo/yolo_baseline/best.pt --data configs/cardetection.yaml --tag yolo_baseline
   python -m src.evaluation.benchmark_fps --weights weights/yolo/yolo_baseline/best.pt
   ```
   → produces `weights/yolo/yolo_baseline/best.pt` (Tu and Loi depend on this) and metrics JSON.
5. **Augmentation ablation** (`notebooks/05`): train with `--aug none/standard/strong`, evaluate each, compare.
6. **Limited-data study** (`notebooks/06`): train with `--fraction 0.1/0.25/0.5/1.0`, plot data-vs-mAP curve.
7. **App backend & real-time optimization:** tune `src/app/inference.py` and the app's inference
   size / frame-skip / confidence so the demo runs at a usable FPS; report the FPS numbers.

---

## Tu — DETR Track · Robustness · Error Analysis · App UI

**Owns:** `src/training/train_detr.py`, `src/evaluation/{evaluate_detr,robustness_eval}.py`,
`src/data/degrade.py`, `src/visualization/{error_gallery,draw_predictions}.py`, app UI.
**Notebooks:** `03_detr_baseline`, `07_robustness`, `08_error_analysis`.

### Midterm tasks (support dataset analysis)
1. **Data-quality analysis** for the report: find and show example images with occlusion, motion
   blur, small/distant signs, and any label problems. Hand these to Loi.
2. **Document the DETR methodology** in the midterm: COCO annotation format, why DETR needs a low
   learning rate, more data, and longer convergence than YOLO.

### Final tasks (application)
3. **DETR baseline** (`notebooks/03_detr_baseline`) — start early, DETR is slow:
   ```bash
   python -m src.training.train_detr --coco data/processed/coco --split cardetection --epochs 50 --name detr_baseline
   python -m src.evaluation.evaluate_detr --model weights/detr/detr_baseline --coco data/processed/coco --split cardetection --set test --tag detr_baseline
   python -m src.evaluation.benchmark_fps --detr weights/detr/detr_baseline
   ```
   → DETR metrics JSON for Loi's comparison. (A lower score than YOLO is still a valid result — explain why.)
4. **Robustness analysis** (`notebooks/07_robustness`) — needs Vinh's `yolo_baseline/best.pt`:
   ```bash
   python -m src.data.degrade --split test --conditions lowlight,motionblur,noise,smallsigns --severity 0.5
   python -m src.evaluation.robustness_eval --weights weights/yolo/yolo_baseline/best.pt --tag yolo_baseline
   ```
   → clean-vs-degraded Δ table; report which driving condition hurts most.
5. **Error analysis** (`notebooks/08_error_analysis`) — needs `yolo_baseline/best.pt`: run
   `error_gallery` (false positives / false negatives / misclassifications) and the per-class AP
   breakdown to find the weakest classes.
6. **App UI:** own the Streamlit layout in `src/app/app.py` — sidebar controls, the warning panel,
   per-class stats table, screenshot/save buttons.

---

## Milestones

| Phase | Who | Output |
|-------|-----|--------|
| **Midterm** | Loi (lead) + Vinh + Tu notes | Dataset-analysis report & presentation (`01_eda`) |
| Final — week 1 | Loi | Data ready; Vinh & Tu unblocked |
| Final — week 2 | Vinh, Tu | YOLO baseline + DETR baseline trained |
| Final — week 3 | Vinh (ablation/limited-data), Tu (robustness/errors) | All experiments done |
| Final — week 4 | Loi (comparison + app), all | Comparison chart, working app, demo video, final report |
