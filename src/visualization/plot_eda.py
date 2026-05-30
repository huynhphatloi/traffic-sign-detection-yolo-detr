"""EDA plots from YOLO labels (M2, plan section 17.3): class balance, box stats, heatmap.

Scans <yolo-root> recursively for label .txt files and matching images, then writes:
  class_distribution.png, box_area_hist.png, aspect_ratio_hist.png,
  objects_per_image.png, center_heatmap.png, small_object_summary.txt

Run: python -m src.visualization.plot_eda --yolo-root data/processed/yolo/cardetection --name cardetection
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.data.common import IMG_EXTS, load_classes  # noqa: E402

SMALL_OBJ_AREA = 0.01  # box area < 1% of image = "small object"


def collect(yolo_root: Path):
    """Return (class_ids, areas, aspects, per_image_counts, centers)."""
    import cv2

    class_ids, areas, aspects, centers = [], [], [], []
    per_image_counts = []
    label_files = sorted(yolo_root.rglob("*.txt"))
    img_index = {p.stem: p for p in yolo_root.rglob("*") if p.suffix.lower() in IMG_EXTS}

    for txt in label_files:
        lines = [ln for ln in txt.read_text().splitlines() if ln.strip()]
        per_image_counts.append(len(lines))
        for ln in lines:
            parts = ln.split()
            if len(parts) != 5:
                continue
            cid, cx, cy, bw, bh = int(parts[0]), *map(float, parts[1:])
            class_ids.append(cid)
            areas.append(bw * bh)
            aspects.append(bw / bh if bh > 0 else 0)
            centers.append((cx, cy))
    return class_ids, areas, aspects, per_image_counts, centers, img_index


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yolo-root", type=Path, required=True)
    ap.add_argument("--name", default="dataset")
    ap.add_argument("--out", type=Path, default=Path("results/plots"))
    args = ap.parse_args()

    classes = load_classes()
    class_ids, areas, aspects, counts, centers, _ = collect(args.yolo_root)
    if not class_ids:
        raise SystemExit(f"No labels found under {args.yolo_root}")

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    areas = np.array(areas)

    # 1) Class distribution
    names = [classes[i] for i in sorted(classes)]
    counts_by_class = [class_ids.count(i) for i in sorted(classes)]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(names, counts_by_class, color="#4287f5")
    ax.set_title(f"[{args.name}] Class distribution")
    ax.set_ylabel("boxes")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout(); fig.savefig(out / f"{args.name}_class_distribution.png", dpi=150); plt.close(fig)

    # 2) Box area
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(areas, bins=40, color="#3cc85a")
    ax.set_title(f"[{args.name}] Bounding-box area (fraction of image)")
    ax.set_xlabel("normalized area"); ax.set_ylabel("count")
    fig.tight_layout(); fig.savefig(out / f"{args.name}_box_area_hist.png", dpi=150); plt.close(fig)

    # 3) Aspect ratio
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(np.clip(aspects, 0, 5), bins=40, color="#c83cc8")
    ax.set_title(f"[{args.name}] Box aspect ratio (w/h)")
    fig.tight_layout(); fig.savefig(out / f"{args.name}_aspect_ratio_hist.png", dpi=150); plt.close(fig)

    # 4) Objects per image
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(counts, bins=range(0, max(counts) + 2), color="#f5a142", align="left")
    ax.set_title(f"[{args.name}] Objects per image")
    ax.set_xlabel("objects"); ax.set_ylabel("images")
    fig.tight_layout(); fig.savefig(out / f"{args.name}_objects_per_image.png", dpi=150); plt.close(fig)

    # 5) Center heatmap
    cx = np.array([c[0] for c in centers]); cy = np.array([c[1] for c in centers])
    heat, _, _ = np.histogram2d(cy, cx, bins=20, range=[[0, 1], [0, 1]])
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(heat, cmap="hot", origin="upper", extent=[0, 1, 1, 0])
    ax.set_title(f"[{args.name}] Sign center heatmap")
    fig.colorbar(im, ax=ax)
    fig.tight_layout(); fig.savefig(out / f"{args.name}_center_heatmap.png", dpi=150); plt.close(fig)

    # 6) Small-object summary
    small = int((areas < SMALL_OBJ_AREA).sum())
    summary = (
        f"dataset: {args.name}\n"
        f"images: {len(counts)}\n"
        f"boxes: {len(areas)}\n"
        f"mean boxes/image: {np.mean(counts):.2f}\n"
        f"small objects (<{SMALL_OBJ_AREA:.0%} area): {small} ({small / len(areas):.1%})\n"
        f"median box area: {np.median(areas):.4f}\n"
    )
    (out / f"{args.name}_small_object_summary.txt").write_text(summary)
    print(summary)
    print(f"[eda] plots written to {out}")


if __name__ == "__main__":
    main()
