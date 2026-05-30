"""Build a failure-case gallery for the error analysis (plan section 21).

Matches predictions to ground truth by IoU and categorizes each image's errors as
false positive / false negative / classification error. Saves the worst images annotated
(GT green, predictions red) plus a CSV tally compare_models-style per error type.

Run: python -m src.visualization.error_gallery --weights weights/yolo/yolo_baseline/best.pt \
        --yolo-root data/processed/yolo/cardetection --split test --n 20
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2

from src.app.inference import YoloDetector
from src.data.common import IMG_EXTS, load_classes, yolo_to_xyxy


def iou(a, b) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    if inter == 0:
        return 0.0
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / (area_a + area_b - inter)


def load_gt(label_path: Path, w: int, h: int):
    gts = []
    if label_path.exists():
        for ln in label_path.read_text().splitlines():
            parts = ln.split()
            if len(parts) != 5:
                continue
            cid, cx, cy, bw, bh = int(parts[0]), *map(float, parts[1:])
            gts.append((cid, yolo_to_xyxy(cx, cy, bw, bh, w, h)))
    return gts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--yolo-root", type=Path, required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--n", type=int, default=20, help="max gallery images to save")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--iou", type=float, default=0.5)
    ap.add_argument("--out", type=Path, default=Path("results/error_cases"))
    args = ap.parse_args()

    classes = load_classes()
    detector = YoloDetector(args.weights)
    images_dir = args.yolo_root / "images" / args.split
    labels_dir = args.yolo_root / "labels" / args.split
    imgs = [p for p in sorted(images_dir.rglob("*")) if p.suffix.lower() in IMG_EXTS]
    if not imgs:
        raise SystemExit(f"No images in {images_dir}")

    args.out.mkdir(parents=True, exist_ok=True)
    tally = {"false_positive": 0, "false_negative": 0, "classification_error": 0}
    scored = []  # (n_errors, image_path, annotated)

    for p in imgs:
        img = cv2.imread(str(p))
        if img is None:
            continue
        h, w = img.shape[:2]
        gts = load_gt(labels_dir / f"{p.stem}.txt", w, h)
        preds = [(d.cls_id, d.xyxy) for d in detector.detect(img, conf=args.conf)]

        matched_gt = set()
        img_errors = 0
        annotated = img.copy()
        for g in gts:  # GT in green
            x1, y1, x2, y2 = (int(v) for v in g[1])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (60, 200, 90), 2)

        for pcid, pbox in preds:
            best_iou, best_j = 0.0, -1
            for j, (gcid, gbox) in enumerate(gts):
                v = iou(pbox, gbox)
                if v > best_iou:
                    best_iou, best_j = v, j
            x1, y1, x2, y2 = (int(v) for v in pbox)
            if best_iou < args.iou:
                tally["false_positive"] += 1; img_errors += 1
                color = (40, 40, 230)  # red FP
            else:
                matched_gt.add(best_j)
                if gts[best_j][0] != pcid:
                    tally["classification_error"] += 1; img_errors += 1
                    color = (40, 160, 230)  # orange wrong-class
                else:
                    color = (200, 200, 200)  # correct (gray)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        n_fn = len(gts) - len(matched_gt)
        tally["false_negative"] += n_fn
        img_errors += n_fn

        if img_errors > 0:
            scored.append((img_errors, p.stem, annotated))

    scored.sort(key=lambda x: -x[0])
    for _, stem, annotated in scored[: args.n]:
        cv2.imwrite(str(args.out / f"err_{stem}.jpg"), annotated)

    with open(args.out / "error_tally.csv", "w", newline="") as f:
        wri = csv.writer(f)
        wri.writerow(["error_type", "count"])
        for k, v in tally.items():
            wri.writerow([k, v])

    print(f"[error_gallery] {tally} | saved {min(len(scored), args.n)} images -> {args.out}")


if __name__ == "__main__":
    main()
