"""Sanity-check converted YOLO labels by drawing boxes on a sample of images.

Catches the classic conversion bug (wrong box format / class id) before training —
see plan risk 27.5. Saves a grid to results/plots/ and can also pop a window.

Run: python -m src.data.visualize_annotations --yolo-root data/processed/yolo/cardetection --split val --n 12
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import cv2

from .common import IMG_EXTS, load_classes, yolo_to_xyxy

# Distinct BGR colors per class id (cycled if more classes than colors).
COLORS = [
    (66, 135, 245), (60, 200, 90), (40, 40, 230), (230, 180, 40),
    (200, 60, 200), (40, 200, 220), (120, 90, 250), (180, 180, 180),
]


def _collect(images_dir: Path) -> list[Path]:
    return [p for p in sorted(images_dir.rglob("*")) if p.suffix.lower() in IMG_EXTS]


def draw(img_path: Path, labels_dir: Path, classes: dict[int, str]):
    im = cv2.imread(str(img_path))
    if im is None:
        return None
    h, w = im.shape[:2]
    label_path = labels_dir / f"{img_path.stem}.txt"
    if label_path.exists():
        for ln in label_path.read_text().splitlines():
            parts = ln.split()
            if len(parts) != 5:
                continue
            cid, cx, cy, bw, bh = int(parts[0]), *map(float, parts[1:])
            xmin, ymin, xmax, ymax = (int(v) for v in yolo_to_xyxy(cx, cy, bw, bh, w, h))
            color = COLORS[cid % len(COLORS)]
            cv2.rectangle(im, (xmin, ymin), (xmax, ymax), color, 2)
            cv2.putText(im, classes.get(cid, str(cid)), (xmin, max(0, ymin - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    return im


def make_grid(images, cols=4, cell=320):
    import numpy as np
    rows = (len(images) + cols - 1) // cols
    grid = np.full((rows * cell, cols * cell, 3), 30, dtype=np.uint8)
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        resized = cv2.resize(im, (cell, cell))
        grid[r * cell:(r + 1) * cell, c * cell:(c + 1) * cell] = resized
    return grid


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yolo-root", type=Path, required=True,
                    help="e.g. data/processed/yolo/cardetection")
    ap.add_argument("--split", default=None, help="train/val/test, or omit for flat layout")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=Path("results/plots/annotation_check.png"))
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    classes = load_classes()
    if args.split:
        images_dir = args.yolo_root / "images" / args.split
        labels_dir = args.yolo_root / "labels" / args.split
    else:
        images_dir = args.yolo_root / "images"
        labels_dir = args.yolo_root / "labels"

    imgs = _collect(images_dir)
    if not imgs:
        raise FileNotFoundError(f"No images in {images_dir}")
    random.Random(args.seed).shuffle(imgs)

    drawn = [im for p in imgs[: args.n] if (im := draw(p, labels_dir, classes)) is not None]
    grid = make_grid(drawn)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.out), grid)
    print(f"[viz] wrote {args.out} ({len(drawn)} samples)")

    if args.show:
        cv2.imshow("annotation check", grid)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
