"""Đo tốc độ suy luận: độ trễ trung vị và phân vị 95.

Báo cáo phân vị 95 chứ không chỉ trung bình, vì với hệ thống thời gian thực thì
trường hợp xấu nhất mới là ràng buộc thật. Một mô hình có trung vị 13 ms nhưng p95
là 60 ms sẽ trượt khung hình, dù con số trung bình nhìn rất đẹp.

Hai chi tiết bắt buộc, thiếu là số đo sai:
  - **Khởi động trước khi bấm giờ.** Lượt chạy đầu chịu chi phí khởi tạo ngữ cảnh
    tính toán và dò thuật toán; tính vào sẽ làm phồng độ trễ.
  - **Đồng bộ hoá sau mỗi lượt trên GPU.** CUDA thực thi bất đồng bộ nên lệnh trả về
    trước khi GPU tính xong; không đồng bộ thì đồng hồ đo thiếu thời gian thật.

CLI:
    python -m src.evaluation.speed
    python -m src.evaluation.speed --models student_kd student_kd_int8
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from src.utils.paths import MODELS, RESULTS_METRICS, ensure_dir

N_WARMUP = 10
N_RUNS = 100
IMGSZ = 640


def _sync(device: str | None) -> None:
    if device and str(device).startswith("cuda"):
        import torch
        if torch.cuda.is_available():
            torch.cuda.synchronize()


def benchmark(weights: Path, imgsz: int = IMGSZ, device: str | None = None,
              warmup: int = N_WARMUP, runs: int = N_RUNS) -> dict:
    """Đo độ trễ trên đầu vào giả. Trả về trung vị, p95, FPS và thiết bị đo."""
    from ultralytics import YOLO

    model = YOLO(str(weights), task="detect")
    dummy = (np.random.rand(imgsz, imgsz, 3) * 255).astype("uint8")
    call = lambda: model.predict(dummy, imgsz=imgsz, device=device, verbose=False)

    for _ in range(warmup):
        call()
    _sync(device)

    samples = []
    for _ in range(runs):
        t0 = time.perf_counter()
        call()
        _sync(device)
        samples.append((time.perf_counter() - t0) * 1000.0)

    arr = np.array(samples)
    median = float(np.median(arr))
    return {
        "weights": str(weights),
        "device": str(device or "auto"),
        "imgsz": imgsz,
        "runs": runs,
        "latency_median_ms": round(median, 2),
        "latency_p95_ms": round(float(np.percentile(arr, 95)), 2),
        "latency_mean_ms": round(float(arr.mean()), 2),
        "fps": round(1000.0 / median, 1) if median else None,
        "size_mib": round(Path(weights).stat().st_size / 1024**2, 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Đo độ trễ suy luận (trung vị + p95).")
    ap.add_argument("--models", nargs="*", default=list(MODELS))
    ap.add_argument("--imgsz", type=int, default=IMGSZ)
    ap.add_argument("--device", default=None)
    ap.add_argument("--runs", type=int, default=N_RUNS)
    ap.add_argument("--out", type=Path, default=RESULTS_METRICS / "speed.json")
    args = ap.parse_args()

    rows = []
    for name in args.models:
        w = MODELS.get(name)
        if w is None:
            raise SystemExit(f"không biết cấu hình '{name}'. Chọn: {', '.join(MODELS)}")
        if not w.exists():
            print(f"[speed] bỏ qua {name}: không thấy {w}")
            continue
        r = benchmark(w, args.imgsz, args.device, runs=args.runs)
        r["model"] = name
        rows.append(r)
        print(f"[speed] {name}: trung vị {r['latency_median_ms']} ms | "
              f"p95 {r['latency_p95_ms']} ms | {r['fps']} FPS | {r['size_mib']} MiB")

    if rows:
        ensure_dir(args.out.parent)
        args.out.write_text(json.dumps(rows, indent=2))
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
