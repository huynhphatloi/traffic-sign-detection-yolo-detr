"""Evaluate a trained DETR checkpoint (plan §8.6) — OWNER: Tu.

TODO (Tu): implement. Run the fine-tuned DETR over a split, compute mAP@0.5 and mAP@0.5:0.95
with torchmetrics (compare in absolute pixel xyxy), merge in FPS/latency from benchmark_fps,
and write the metrics JSON.
Expected output: results/metrics/detr_baseline.json
Reuse: transformers Detr*, torchmetrics MeanAveragePrecision, torchvision CocoDetection,
       src.evaluation.benchmark_fps.benchmark_detr, src.utils.paths.

This file is an intentional stub — see TODO.md.
"""
