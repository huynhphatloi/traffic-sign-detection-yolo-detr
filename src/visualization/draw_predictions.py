"""Save side-by-side ground-truth vs prediction images for a YOLO model (qualitative check).

For each sampled test image: left = GT boxes, right = model predictions. Useful for the
report's qualitative section and for spotting systematic errors before the full error gallery.

Run: python -m src.visualization.draw_predictions --weights weights/yolo/yolo_baseline/best.pt \
        --yolo-root data/processed/yolo/cardetection --split test --n 12
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import cv2
import numpy as np

from src.app.inference import YoloDetector, draw_detections
from src.data.common import IMG_EXTS, load_classes, yolo_to_xyxy


def draw_gt(img, label_path, classes):
    out = img.copy()
    h, w = img.shape[:2]
    if label_path.exists():
        for ln in label_path.read_text().splitlines():
            parts = ln.split()
            if len(parts) != 5:
                continue
            cid, cx, cy, bw, bh = int(parts[0]), *map(float, parts[1:])
            x1, y1, x2, y2 = (int(v) for v in yolo_to_xyxy(cx, cy, bw, bh, w, h))
            cv2.rectangle(out, (x1, y1), (x2, y2), (60, 200, 90), 2)
            cv2.putText(out, classes.get(cid, str(cid)), (x1, max(0, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 200, 90), 1, cv2.LINE_AA)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--yolo-root", type=Path, required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=Path("results/predictions"))
    args = ap.parse_args()

    classes = load_classes()
    detector = YoloDetector(args.weights)
    images_dir = args.yolo_root / "images" / args.split
    labels_dir = args.yolo_root / "labels" / args.split
    imgs = [p for p in sorted(images_dir.rglob("*")) if p.suffix.lower() in IMG_EXTS]
    if not imgs:
        raise SystemExit(f"No images in {images_dir}")
    random.Random(args.seed).shuffle(imgs)

    args.out.mkdir(parents=True, exist_ok=True)
    for p in imgs[: args.n]:
        img = cv2.imread(str(p))
        if img is None:
            continue
        gt = draw_gt(img, labels_dir / f"{p.stem}.txt", classes)
        pred = draw_detections(img, detector.detect(img, conf=args.conf))
        h = max(gt.shape[0], pred.shape[0])
        canvas = np.full((h, gt.shape[1] + pred.shape[1] + 10, 3), 30, np.uint8)
        canvas[:gt.shape[0], :gt.shape[1]] = gt
        canvas[:pred.shape[0], gt.shape[1] + 10:] = pred
        cv2.imwrite(str(args.out / f"cmp_{p.stem}.jpg"), canvas)
    print(f"[draw_predictions] wrote GT|pred comparisons to {args.out}")


if __name__ == "__main__":
    main()
