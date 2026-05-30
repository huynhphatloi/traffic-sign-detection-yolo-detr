"""Build COCO-format JSON (for DETR) from the split YOLO datasets.

Input : data/processed/yolo/<dataset>/{images,labels}/{train,val,test}
Output: data/processed/coco/<dataset>/{train,val,test}.json
        (annotations reference the existing image files by absolute path + file_name)

Run: python -m src.data.convert_to_coco --yolo-root data/processed/yolo --out data/processed/coco
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
from tqdm import tqdm

from .common import IMG_EXTS, load_classes, yolo_to_xyxy

SPLITS = ("train", "val", "test")


def build_split(images_dir: Path, labels_dir: Path, classes: dict[int, str]) -> dict:
    categories = [{"id": cid, "name": name} for cid, name in sorted(classes.items())]
    coco = {"images": [], "annotations": [], "categories": categories}

    img_id = ann_id = 0
    imgs = [p for p in sorted(images_dir.iterdir()) if p.suffix.lower() in IMG_EXTS]
    for img_path in tqdm(imgs, desc=f"coco:{images_dir.parent.parent.name}/{images_dir.name}"):
        im = cv2.imread(str(img_path))
        if im is None:
            continue
        h, w = im.shape[:2]
        coco["images"].append(
            {"id": img_id, "file_name": img_path.name,
             "abs_path": str(img_path.resolve()), "width": w, "height": h}
        )

        label_path = labels_dir / f"{img_path.stem}.txt"
        if label_path.exists():
            for ln in label_path.read_text().splitlines():
                parts = ln.split()
                if len(parts) != 5:
                    continue
                cid, cx, cy, bw, bh = int(parts[0]), *map(float, parts[1:])
                xmin, ymin, xmax, ymax = yolo_to_xyxy(cx, cy, bw, bh, w, h)
                bw_px, bh_px = xmax - xmin, ymax - ymin
                coco["annotations"].append({
                    "id": ann_id, "image_id": img_id, "category_id": cid,
                    "bbox": [xmin, ymin, bw_px, bh_px],  # COCO = [x, y, w, h]
                    "area": bw_px * bh_px, "iscrowd": 0,
                })
                ann_id += 1
        img_id += 1
    return coco


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yolo-root", type=Path, default=Path("data/processed/yolo"))
    ap.add_argument("--out", type=Path, default=Path("data/processed/coco"))
    ap.add_argument("--datasets", nargs="+", default=["cardetection"])
    args = ap.parse_args()

    classes = load_classes()
    for name in args.datasets:
        ds_root = args.yolo_root / name
        for split in SPLITS:
            images_dir = ds_root / "images" / split
            labels_dir = ds_root / "labels" / split
            if not images_dir.is_dir():
                continue
            coco = build_split(images_dir, labels_dir, classes)
            out_dir = args.out / name
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{split}.json"
            out_file.write_text(json.dumps(coco))
            print(f"[coco] {name}/{split}: {len(coco['images'])} imgs, "
                  f"{len(coco['annotations'])} anns -> {out_file}")


if __name__ == "__main__":
    main()
