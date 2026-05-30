"""Shared helpers for the data pipeline: class loading and bbox math.

Used by all conversion / visualization scripts so the dataset's class system
(configs/classes.yaml) lives in exactly one place.
"""
from __future__ import annotations

from pathlib import Path

import yaml

# Resolve project paths relative to this file (src/data/common.py -> project root).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = PROJECT_ROOT / "configs"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_classes(path: Path | str = CONFIGS_DIR / "classes.yaml") -> dict[int, str]:
    """Return {id: name} for the dataset's class system."""
    with open(path) as f:
        data = yaml.safe_load(f)
    names = data["names"]
    # YAML may give a dict {0: name} or a list [name, ...]; normalize to dict.
    if isinstance(names, list):
        return {i: n for i, n in enumerate(names)}
    return {int(k): v for k, v in names.items()}


def class_name_to_id(classes: dict[int, str] | None = None) -> dict[str, int]:
    classes = classes or load_classes()
    return {name: cid for cid, name in classes.items()}


def voc_to_yolo(xmin: float, ymin: float, xmax: float, ymax: float, w: int, h: int):
    """PASCAL VOC pixel box -> normalized YOLO (cx, cy, bw, bh) in [0, 1]."""
    cx = ((xmin + xmax) / 2.0) / w
    cy = ((ymin + ymax) / 2.0) / h
    bw = (xmax - xmin) / w
    bh = (ymax - ymin) / h
    return cx, cy, bw, bh


def yolo_to_xyxy(cx: float, cy: float, bw: float, bh: float, w: int, h: int):
    """Normalized YOLO box -> pixel (xmin, ymin, xmax, ymax)."""
    xmin = (cx - bw / 2.0) * w
    ymin = (cy - bh / 2.0) * h
    xmax = (cx + bw / 2.0) * w
    ymax = (cy + bh / 2.0) * h
    return xmin, ymin, xmax, ymax


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))
