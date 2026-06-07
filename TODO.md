# Roadmap & Contributing

This project is built as **thin notebook orchestration over `src/` modules**. Some modules are
implemented and run today; others are stubs waiting to be filled in. Contributions are welcome —
pick an unimplemented module below, implement it to match its docstring and expected outputs, then
un-comment the matching section in
[`notebooks/traffic_sign_detection_pipeline.ipynb`](notebooks/traffic_sign_detection_pipeline.ipynb).

Reuse the existing helpers instead of re-deriving them:
- `src.data.inspect_dataset` exposes `list_images`, `label_path_for`, `parse_label_file`, `iter_pairs`.
- `src.utils.paths` is the central path registry (all input/output locations).
- `src.utils.plotting` holds shared plot styling/saving helpers.

Keep the dataset as-is: `pkdarabi/cardetection`, **15 native classes**, no remapping.

## Implemented ✅

- `src/utils/{paths,plotting}.py`
- `src/data/inspect_dataset.py` → `results/tables/dataset_summary.csv` (detects format, syncs configs)
- `src/data/visualize_annotations.py` → `results/samples/annotated_train_samples/`
- `src/training/train_yolo.py` → `weights/yolo/yolo_baseline/best.pt`
- `src/evaluation/evaluate_yolo.py` + `benchmark_fps.py` → `results/metrics/yolo_baseline.json`

## Open tasks 🚧

**EDA** (notebook §2)
- [ ] `src/eda/class_distribution.py` — counts + bar chart + imbalance ratio
      → `results/eda/class_distribution.png`, `results/tables/class_distribution.csv`
- [ ] `src/eda/bbox_statistics.py` — box area/wh/aspect + small/medium/large split; also a shared
      `collect_boxes()` collector → `results/eda/bbox_*.png`, `results/tables/bbox_size_categories.csv`
- [ ] `src/eda/image_statistics.py` — per-split counts, resolution, objects-per-image
      → `results/eda/{images_per_split,image_resolution,objects_per_image}.png`, `results/tables/image_statistics.csv`
- [ ] `src/eda/heatmap_analysis.py` — object-center heatmap → `results/eda/object_center_heatmap.png`

**Data quality** (notebook §3)
- [ ] `src/data/validate_labels.py` — missing/empty/invalid/corrupt/duplicate checks
      → `results/tables/data_quality_report.csv`; plus a difficult-sample gallery (small/blurry/low-light)

**DETR baseline** (notebook §5, GPU)
- [ ] `src/data/convert_to_coco.py` — YOLO TXT → COCO JSON → `data/coco/instances_{split}.json`
- [ ] `src/training/train_detr.py` — fine-tune `facebook/detr-resnet-50` → `weights/detr/detr_baseline/`
- [ ] `src/evaluation/evaluate_detr.py` — mAP + FPS → `results/metrics/detr_baseline.json`

**Comparison** (notebook §6)
- [ ] `src/evaluation/compare_models.py` — collect both metrics JSONs → `results/tables/comparison.csv`
