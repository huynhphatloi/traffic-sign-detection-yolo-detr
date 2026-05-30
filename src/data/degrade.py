"""Synthesize degraded driving conditions on a YOLO split for robustness analysis.

The dataset has no native night/rain/blur splits, so we simulate them (the project's
robustness section): take a clean split and apply photometric/blur/noise/resolution
degradations, producing data/degraded/<condition>/{images,labels}/<split> that mirrors
the YOLO layout. Every degradation here is GEOMETRY-PRESERVING (no crop/translate/flip),
so the original labels are valid unchanged and are simply copied -> a fair clean-vs-degraded
comparison for the same boxes.

Conditions (intensity controlled by --severity in [0,1]):
  lowlight    multiplicative darkening + gamma (distant/night driving)
  motionblur  directional (horizontal) kernel blur (camera/vehicle motion)
  noise       additive Gaussian sensor noise (rain/low-light grain)
  smallsigns  downscale-then-upscale to destroy detail (distant signs)

Run: python -m src.data.degrade --split test \
        --conditions lowlight,motionblur,noise,smallsigns --severity 0.5
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

from .common import IMG_EXTS


def lowlight(img: np.ndarray, s: float) -> np.ndarray:
    """Darken: scale brightness down and push gamma. s=0 -> unchanged, s=1 -> very dark."""
    scale = 1.0 - 0.7 * s            # 1.0 .. 0.3
    gamma = 1.0 + 1.5 * s            # 1.0 .. 2.5
    x = (img.astype(np.float32) / 255.0) * scale
    x = np.power(x, gamma)
    return np.clip(x * 255.0, 0, 255).astype(np.uint8)


def motionblur(img: np.ndarray, s: float) -> np.ndarray:
    """Horizontal motion blur; kernel length grows with severity (min 3, odd)."""
    h, w = img.shape[:2]
    k = max(3, int(round(s * 0.06 * w)))
    if k % 2 == 0:
        k += 1
    kernel = np.zeros((k, k), np.float32)
    kernel[k // 2, :] = 1.0 / k
    return cv2.filter2D(img, -1, kernel)


def noise(img: np.ndarray, s: float) -> np.ndarray:
    """Additive Gaussian noise; std up to ~50 levels at s=1."""
    sigma = 50.0 * s
    g = np.random.normal(0.0, sigma, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + g, 0, 255).astype(np.uint8)


def smallsigns(img: np.ndarray, s: float) -> np.ndarray:
    """Downscale then upscale back to lose high-frequency detail (distant-sign proxy)."""
    h, w = img.shape[:2]
    factor = 1.0 - 0.75 * s          # 1.0 .. 0.25
    nh, nw = max(1, int(h * factor)), max(1, int(w * factor))
    small = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


CONDITIONS = {
    "lowlight": lowlight,
    "motionblur": motionblur,
    "noise": noise,
    "smallsigns": smallsigns,
}


def degrade_split(yolo_root: Path, split: str, condition: str, severity: float,
                  out_root: Path, seed: int) -> None:
    fn = CONDITIONS[condition]
    img_src = yolo_root / "images" / split
    lbl_src = yolo_root / "labels" / split
    img_dst = out_root / condition / "images" / split
    lbl_dst = out_root / condition / "labels" / split
    img_dst.mkdir(parents=True, exist_ok=True)
    lbl_dst.mkdir(parents=True, exist_ok=True)

    np.random.seed(seed)
    imgs = [p for p in sorted(img_src.iterdir()) if p.suffix.lower() in IMG_EXTS]
    if not imgs:
        raise FileNotFoundError(f"No images in {img_src}")
    for p in tqdm(imgs, desc=f"{condition}:{split}"):
        im = cv2.imread(str(p))
        if im is None:
            continue
        cv2.imwrite(str(img_dst / p.name), fn(im, severity))
        lbl = lbl_src / f"{p.stem}.txt"
        if lbl.exists():                         # labels unchanged (geometry preserved)
            shutil.copy2(lbl, lbl_dst / lbl.name)
    print(f"[degrade] {condition} (s={severity}) -> {img_dst}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yolo-root", type=Path, default=Path("data/processed/yolo/cardetection"))
    ap.add_argument("--split", default="test", choices=["train", "val", "test"])
    ap.add_argument("--conditions", default="lowlight,motionblur,noise,smallsigns")
    ap.add_argument("--severity", type=float, default=0.5, help="degradation intensity in [0,1]")
    ap.add_argument("--out", type=Path, default=Path("data/degraded"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    unknown = [c for c in conditions if c not in CONDITIONS]
    if unknown:
        raise SystemExit(f"Unknown condition(s) {unknown}; choose from {list(CONDITIONS)}")

    for cond in conditions:
        degrade_split(args.yolo_root, args.split, cond, args.severity, args.out, args.seed)


if __name__ == "__main__":
    main()
