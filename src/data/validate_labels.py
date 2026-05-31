"""Annotation / data-quality validation (plan §8.2) — OWNER: Tu.

TODO (Tu): implement. Scan the dataset and flag every quality issue, then write a per-image
report + a printed summary. Checks: missing image, missing label, empty label, invalid class
id, box outside [0,1], zero-width/height box, duplicate image name, corrupt/unreadable image.
Expected output: results/tables/data_quality_report.csv
Reuse: src.data.inspect_dataset.{iter_pairs,parse_label_file}, cv2 for corrupt-image checks.

This file is an intentional stub — see TODO.md.
"""
