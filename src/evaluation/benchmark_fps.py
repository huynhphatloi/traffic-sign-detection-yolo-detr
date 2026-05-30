"""Benchmark inference speed (FPS, latency) and model size — deployment metrics (section 15.2).

Works for YOLO (.pt) and DETR (saved dir). Warms up, then times N forward passes on a
synthetic frame and writes results/metrics/<tag>_speed.json.

Example:
  python -m src.evaluation.benchmark_fps --weights weights/yolo/yolo_baseline/best.pt
  python -m src.evaluation.benchmark_fps --detr weights/detr/detr_baseline
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def _dir_size_mb(path: Path) -> float:
    if path.is_file():
        return path.stat().st_size / 1e6
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) / 1e6


def bench_yolo(weights: str, imgsz: int, runs: int, device):
    import numpy as np
    from ultralytics import YOLO

    model = YOLO(weights)
    frame = np.random.randint(0, 255, (imgsz, imgsz, 3), dtype="uint8")
    for _ in range(5):  # warmup
        model.predict(frame, imgsz=imgsz, device=device, verbose=False)
    t0 = time.perf_counter()
    for _ in range(runs):
        model.predict(frame, imgsz=imgsz, device=device, verbose=False)
    elapsed = time.perf_counter() - t0
    return elapsed, _dir_size_mb(Path(weights))


def bench_detr(model_dir: str, imgsz: int, runs: int, device):
    import numpy as np
    import torch
    from transformers import DetrForObjectDetection, DetrImageProcessor

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    processor = DetrImageProcessor.from_pretrained(model_dir)
    model = DetrForObjectDetection.from_pretrained(model_dir).to(device).eval()
    frame = np.random.randint(0, 255, (imgsz, imgsz, 3), dtype="uint8")
    inputs = processor(images=frame, return_tensors="pt").to(device)
    with torch.no_grad():
        for _ in range(5):
            model(**inputs)
        t0 = time.perf_counter()
        for _ in range(runs):
            model(**inputs)
        elapsed = time.perf_counter() - t0
    return elapsed, _dir_size_mb(Path(model_dir))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", help="YOLO .pt")
    ap.add_argument("--detr", help="DETR saved dir")
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--runs", type=int, default=100)
    ap.add_argument("--device", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--out", type=Path, default=Path("results/metrics"))
    args = ap.parse_args()

    if args.weights:
        elapsed, size_mb = bench_yolo(args.weights, args.imgsz, args.runs, args.device)
        model_kind, src = "yolo", args.weights
    elif args.detr:
        elapsed, size_mb = bench_detr(args.detr, args.imgsz, args.runs, args.device)
        model_kind, src = "detr", args.detr
    else:
        ap.error("pass --weights (YOLO) or --detr (DETR)")

    fps = args.runs / elapsed
    latency_ms = 1000.0 * elapsed / args.runs
    speed = {
        "model": model_kind, "source": str(src), "device": str(args.device or "auto"),
        "imgsz": args.imgsz, "runs": args.runs,
        "fps": round(fps, 2), "latency_ms": round(latency_ms, 2),
        "model_size_mb": round(size_mb, 2),
    }

    tag = args.tag or Path(src).stem if model_kind == "yolo" else (args.tag or Path(src).name)
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{tag}_speed.json"
    out_file.write_text(json.dumps(speed, indent=2))
    print(f"[bench] {model_kind} FPS={fps:.1f} latency={latency_ms:.1f}ms "
          f"size={size_mb:.1f}MB -> {out_file}")


if __name__ == "__main__":
    main()
