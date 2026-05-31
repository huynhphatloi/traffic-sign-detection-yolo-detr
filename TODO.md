# Phase 1 (Midterm) — Team TODO

Tick a box when done: `- [ ]` → `- [x]`. Each task names the file(s) to build and the output it
produces. Run order: **Loi → (Vinh ‖ Tu)**. Training tasks need a GPU (Colab).

> Loi's data pipeline + YOLO baseline are **done and runnable**. Vinh and Tu: your files are
> stubs (title + task description in the docstring) — implement them, then run your notebook.

---

## Loi — data pipeline · YOLO · integration  ✅ done

- [x] Repo scaffold, configs, `.gitignore`, `requirements.txt`
- [x] `src/utils/{paths,plotting}.py`
- [x] `src/data/inspect_dataset.py` → `results/tables/dataset_summary.csv` (detects format, syncs configs)
- [x] `src/data/visualize_annotations.py` → `results/samples/annotated_train_samples/`
- [x] `src/training/train_yolo.py` → `weights/yolo/yolo_baseline/best.pt`
- [x] `src/evaluation/evaluate_yolo.py` + `benchmark_fps.py` → `results/metrics/yolo_baseline.json`
- [x] Notebooks `00_colab_setup`, `01_dataset_inspection`, `04_yolo_baseline`
- [x] `README.md`, `reports/midterm_report.md` skeleton
- [ ] Run `04_yolo_baseline` on Colab and commit the YOLO metrics JSON
- [ ] Assemble the midterm report + slides once Vinh & Tu deliver their sections

## Vinh — EDA · data mining · initial comparison  ⬜ to do

- [ ] `src/eda/bbox_statistics.py` — implement `collect_boxes()` + box area/wh/aspect/size plots
      → `results/eda/bbox_*.png`, `results/tables/bbox_size_categories.csv`
- [ ] `src/eda/class_distribution.py` — counts + bar chart + imbalance ratio
      → `results/eda/class_distribution.png`, `results/tables/class_distribution.csv`
- [ ] `src/eda/image_statistics.py` — per-split counts, resolution, objects-per-image
      → `results/eda/{images_per_split,image_resolution,objects_per_image}.png`, `results/tables/image_statistics.csv`
- [ ] `src/eda/heatmap_analysis.py` — object-center heatmap → `results/eda/object_center_heatmap.png`
- [ ] `src/evaluation/compare_models.py` — initial YOLO vs DETR table → `results/tables/comparison.csv`
- [ ] Run notebook `02_eda_analysis` (and `06_comparison_analysis` after baselines exist)
- [ ] Write the EDA section of `reports/midterm_report.md` (§3) → hand to Loi

## Tu — data quality · DETR baseline · robustness plan  ⬜ to do

- [ ] `src/data/validate_labels.py` — quality checks → `results/tables/data_quality_report.csv`
- [ ] `src/data/convert_to_coco.py` — YOLO TXT → COCO JSON → `data/coco/instances_{split}.json`
- [ ] `src/training/train_detr.py` — fine-tune detr-resnet-50 → `weights/detr/detr_baseline/`  *(GPU)*
- [ ] `src/evaluation/evaluate_detr.py` — mAP + FPS → `results/metrics/detr_baseline.json`
- [ ] Run notebooks `03_data_quality` and `05_detr_baseline`
- [ ] Difficult-sample gallery (small / blurry / low-light signs) in `03_data_quality`
- [ ] Write the Data Quality section (§4) + literature review + robustness/data-efficiency plan
      (§6) of `reports/midterm_report.md` → hand to Loi

---

### Notes
- Build on Loi's helpers — don't re-derive: `src.data.inspect_dataset` exposes
  `list_images`, `label_path_for`, `parse_label_file`, `iter_pairs`; `src.utils.paths` has all paths.
- Keep the teacher dataset (`pkdarabi/cardetection`, 15 classes) — do not swap it.
- Full robustness + data-efficiency **experiments**, the Gradio app, and Hugging Face deployment
  are **Phase 2** (not in this TODO).
