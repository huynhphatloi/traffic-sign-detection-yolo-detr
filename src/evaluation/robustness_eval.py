"""Evaluate one YOLO checkpoint across clean + degraded test sets (robustness analysis).

Pairs with src.data.degrade: after generating data/degraded/<condition>/..., this runs
Ultralytics validation on the clean test set and on each degraded set, then tabulates the
drop in mAP@0.5 / mAP@0.5:0.95 / recall caused by each driving condition.

For each set it writes a temporary Ultralytics data .yaml (pointing `val` at that set's
images) so `model.val()` measures performance on exactly those images, with the unchanged
ground-truth labels.

Outputs:
  results/robustness/<tag>_robustness.csv   one row per condition with metrics + delta vs clean

Example:
  python -m src.evaluation.robustness_eval --weights weights/yolo/yolo_baseline/best.pt \
      --clean-root data/processed/yolo/cardetection --degraded-root data/degraded --tag yolo_baseline
"""
from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

import yaml

from src.data.common import load_classes


def _data_yaml(images_split_dir: Path, names: list[str], tmp: Path) -> Path:
    """Write a one-off Ultralytics data.yaml whose val/test point at images_split_dir.

    Ultralytics derives label paths by swapping `/images/` -> `/labels/` in the image path,
    so the degraded layout (images/<split> + labels/<split>) is found automatically.
    """
    parent = images_split_dir.parent.parent          # .../<set>/images/<split> -> .../<set>
    split = images_split_dir.name
    cfg = {
        "path": str(parent.resolve()),
        "train": f"images/{split}",
        "val": f"images/{split}",
        "test": f"images/{split}",
        "nc": len(names),
        "names": names,
    }
    out = tmp / f"{parent.name}_{split}.yaml"
    out.write_text(yaml.safe_dump(cfg, sort_keys=False))
    return out


def _validate(model, data_yaml: Path, imgsz: int, device) -> dict:
    res = model.val(data=str(data_yaml), split="val", imgsz=imgsz, device=device)
    return {
        "map50": float(res.box.map50),
        "map50_95": float(res.box.map),
        "precision": float(res.box.mp),
        "recall": float(res.box.mr),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--clean-root", type=Path, default=Path("data/processed/yolo/cardetection"))
    ap.add_argument("--degraded-root", type=Path, default=Path("data/degraded"))
    ap.add_argument("--split", default="test", choices=["train", "val", "test"])
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--device", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--out", type=Path, default=Path("results/robustness"))
    args = ap.parse_args()

    from ultralytics import YOLO

    names = [load_classes()[i] for i in sorted(load_classes())]
    model = YOLO(args.weights)
    tag = args.tag or Path(args.weights).parent.name

    rows = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        clean_yaml = _data_yaml(args.clean_root / "images" / args.split, names, tmp)
        clean = _validate(model, clean_yaml, args.imgsz, args.device)
        clean.update({"condition": "clean", "d_map50": 0.0, "d_map50_95": 0.0, "d_recall": 0.0})
        rows.append(clean)
        print(f"[robust] clean: mAP50={clean['map50']:.4f}")

        conditions = sorted(p.name for p in args.degraded_root.iterdir()
                            if p.is_dir() and (p / "images" / args.split).is_dir())
        for cond in conditions:
            images_split = args.degraded_root / cond / "images" / args.split
            m = _validate(model, _data_yaml(images_split, names, tmp), args.imgsz, args.device)
            m.update({
                "condition": cond,
                "d_map50": m["map50"] - clean["map50"],
                "d_map50_95": m["map50_95"] - clean["map50_95"],
                "d_recall": m["recall"] - clean["recall"],
            })
            rows.append(m)
            print(f"[robust] {cond}: mAP50={m['map50']:.4f} (Δ {m['d_map50']:+.4f})")

    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{tag}_robustness.csv"
    fields = ["condition", "map50", "map50_95", "precision", "recall",
              "d_map50", "d_map50_95", "d_recall"]
    with open(out_file, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})
    print(f"[robust] wrote {out_file} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
