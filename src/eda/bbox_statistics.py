"""Bounding-box statistics (plan §8.4) — OWNER: Vinh.

TODO (Vinh): implement. Box size (area), width/height, aspect ratio, and the small/medium/
large split (boxes are normalized, so area = w*h and aspect = w/h need no image decode).
Also provide `collect_boxes(root)` — the shared box collector reused by class_distribution
and heatmap_analysis (return one row per box: split, image, cls, xc, yc, w, h, area, aspect).
Expected outputs: results/eda/{bbox_area,bbox_wh,bbox_aspect_ratio,bbox_size_categories}.png,
                  results/tables/bbox_size_categories.csv
Reuse: src.data.inspect_dataset.{list_images,label_path_for,parse_label_file}.

This file is an intentional stub — see TODO.md.
"""
