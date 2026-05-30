"""Evaluate a trained YOLO checkpoint and save unified metrics JSON.

Writes results/metrics/<tag>.json with mAP@0.5, mAP@0.5:0.95, precision, recall, and
per-class AP — the schema compare_models.py expects.

Example:
  python -m src.evaluation.evaluate_yolo --weights weights/yolo/yolo_baseline/best.pt \
      --data configs/cardetection.yaml --split test --tag yolo_baseline
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--split", default="test", choices=["train", "val", "test"])
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--device", default=None)
    ap.add_argument("--tag", default=None, help="metrics filename (default: weights parent name)")
    ap.add_argument("--out", type=Path, default=Path("results/metrics"))
    args = ap.parse_args()

    from ultralytics import YOLO

    model = YOLO(args.weights)
    res = model.val(data=args.data, split=args.split, imgsz=args.imgsz, device=args.device)

    names = res.names  # {id: name}
    per_class_ap = {}
    try:
        for i, cid in enumerate(res.ap_class_index):
            per_class_ap[names[int(cid)]] = float(res.box.ap50[i])
    except Exception:
        pass

    metrics = {
        "model": "yolo",
        "weights": str(args.weights),
        "data": str(args.data),
        "split": args.split,
        "map50": float(res.box.map50),
        "map50_95": float(res.box.map),
        "precision": float(res.box.mp),
        "recall": float(res.box.mr),
        "per_class_ap50": per_class_ap,
    }

    tag = args.tag or Path(args.weights).parent.name
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{tag}.json"
    out_file.write_text(json.dumps(metrics, indent=2))
    print(f"[eval_yolo] mAP50={metrics['map50']:.4f} mAP50-95={metrics['map50_95']:.4f} "
          f"P={metrics['precision']:.4f} R={metrics['recall']:.4f} -> {out_file}")


if __name__ == "__main__":
    main()
