"""Train an Ultralytics YOLO detector on the cardetection dataset (YOLO baseline).

Also supports the augmentation ablation via --aug {none,standard,strong} and the
limited-data study via --fraction.

After training, the best checkpoint is copied to weights/yolo/<name>/best.pt so the rest
of the pipeline (evaluate, robustness, app) can find it predictably.

Examples:
  python -m src.training.train_yolo --data configs/cardetection.yaml --name yolo_baseline
  python -m src.training.train_yolo --data configs/cardetection.yaml --aug strong --name yolo_aug_strong
  python -m src.training.train_yolo --data configs/cardetection.yaml --fraction 0.25 --name yolo_25pct
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

# Augmentation presets. YOLO flips are OFF by default because many signs are directional
# (plan section 14): flipping would create unrealistic mirror-image signs.
AUG_PRESETS = {
    "none": dict(hsv_h=0, hsv_s=0, hsv_v=0, translate=0, scale=0, fliplr=0,
                 mosaic=0, mixup=0, erasing=0),
    "standard": dict(hsv_h=0.015, hsv_s=0.5, hsv_v=0.4, translate=0.1, scale=0.4,
                     fliplr=0, mosaic=0.5, mixup=0, erasing=0.2),
    "strong": dict(hsv_h=0.02, hsv_s=0.7, hsv_v=0.5, translate=0.15, scale=0.6,
                   fliplr=0, mosaic=1.0, mixup=0.1, erasing=0.4),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="path to an Ultralytics data .yaml")
    ap.add_argument("--model", default="yolov8s.pt", help="base weights (yolov8n/s, yolo11n/s ...)")
    ap.add_argument("--name", required=True, help="run name; weights saved to weights/yolo/<name>")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr0", type=float, default=0.01)
    ap.add_argument("--aug", choices=list(AUG_PRESETS), default="standard")
    ap.add_argument("--fraction", type=float, default=1.0, help="limited-label fraction (0-1]")
    ap.add_argument("--device", default=None, help="e.g. 0 / cpu (default: auto)")
    ap.add_argument("--project", default="runs/yolo")
    args = ap.parse_args()

    from ultralytics import YOLO  # imported lazily so --help works without the dep

    model = YOLO(args.model)
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        lr0=args.lr0,
        fraction=args.fraction,
        device=args.device,
        project=args.project,
        name=args.name,
        exist_ok=True,
        **AUG_PRESETS[args.aug],
    )

    # Mirror the best checkpoint into weights/yolo/<name>/best.pt for downstream scripts.
    save_dir = Path(results.save_dir)
    best = save_dir / "weights" / "best.pt"
    dest = Path("weights/yolo") / args.name
    dest.mkdir(parents=True, exist_ok=True)
    if best.exists():
        shutil.copy2(best, dest / "best.pt")
        print(f"[train_yolo] best weights -> {dest / 'best.pt'}")
    print(f"[train_yolo] run dir: {save_dir}")


if __name__ == "__main__":
    main()
