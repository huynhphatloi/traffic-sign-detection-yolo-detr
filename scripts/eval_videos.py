"""Chạy pipeline phát hiện của ứng dụng trình diễn trên video đường thật.

Video trong dataset/test/ KHÔNG có nhãn thật, nên script này cố ý KHÔNG tính mAP.
Nó chỉ đo các đại lượng quan sát được mà không cần nhãn:

  - số phát hiện trên mỗi khung hình,
  - phân bố độ tin cậy,
  - phân bố KÍCH THƯỚC của vật thể được phát hiện (theo % cạnh khung hình),
  - phân bố lớp.

Mục đích là kiểm chứng giả thuyết trung tâm của báo cáo: nếu mô hình yếu ở vật thể
nhỏ, thì việc tăng kích thước ảnh đầu vào phải làm lộ ra thêm các phát hiện có cạnh
nhỏ, chứ không chỉ làm tăng đều số phát hiện ở mọi cỡ.

    python scripts/eval_videos.py --stride 10
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "app"))

# Dùng lại đúng logic của ứng dụng trình diễn, không cài đặt lại.
import importlib.util

_spec = importlib.util.spec_from_file_location("tsd_app", REPO / "app" / "streamlit_app.py")
_app = importlib.util.module_from_spec(_spec)
sys.modules["tsd_app"] = _app
_spec.loader.exec_module(_app)


def make_settings(conf, imgsz, drop_bottom_pct, use_tiling, tile=640, overlap=0.2):
    return {
        "conf": conf, "iou": 0.70, "imgsz": imgsz,
        "drop_bottom_pct": drop_bottom_pct,
        "use_tiling": use_tiling, "tile": tile, "overlap": overlap,
    }


CONFIGS = {
    "A. imgsz 640, conf 0.35 (mặc định cũ)":  make_settings(0.35, 640,  0,  False),
    "B. imgsz 1280, conf 0.20 (mặc định mới)": make_settings(0.20, 1280, 30, False),
    "C. imgsz 1280 + tiled":                   make_settings(0.20, 1280, 30, True),
}


def run_video(path: Path, settings: dict, stride: int, use_roi: bool):
    cap = cv2.VideoCapture(str(path))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    rows, frames_done, idx = [], 0, 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % stride == 0:
            dets = _app.detect_rows(frame, settings, use_roi=use_roi)
            for d in dets:
                w = abs(d["x2"] - d["x1"])
                h = abs(d["y2"] - d["y1"])
                rows.append({
                    "video": path.name, "frame": idx, "cls": d["class"],
                    "conf": d["confidence"],
                    # cạnh hình học của hộp, quy về % cạnh khung hình gốc
                    "side_pct": 100.0 * float(np.sqrt(max(w * h, 1e-9))) / max(W, H),
                    "side_px": float(np.sqrt(max(w * h, 1e-9))),
                })
            frames_done += 1
        idx += 1
    cap.release()
    return rows, frames_done, (W, H)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stride", type=int, default=10, help="xử lý 1 trong mỗi N khung hình")
    ap.add_argument("--out", type=Path, default=REPO / "results" / "video_eval")
    args = ap.parse_args()

    videos = sorted((REPO / "dataset" / "test").glob("*.mp4"))
    if not videos:
        sys.exit("không tìm thấy video nào trong dataset/test/")

    args.out.mkdir(parents=True, exist_ok=True)
    summary, all_rows = [], []

    for name, st in CONFIGS.items():
        for v in videos:
            rows, nframes, (W, H) = run_video(v, st, args.stride, use_roi=st["drop_bottom_pct"] > 0)
            for r in rows:
                r["config"] = name
            all_rows.extend(rows)
            confs = [r["conf"] for r in rows]
            sides = [r["side_pct"] for r in rows]
            summary.append({
                "config": name, "video": v.name, "resolution": f"{W}x{H}",
                "frames": nframes, "detections": len(rows),
                "det_per_frame": round(len(rows) / max(nframes, 1), 3),
                "conf_mean": round(float(np.mean(confs)), 4) if confs else None,
                "side_pct_median": round(float(np.median(sides)), 3) if sides else None,
                "side_pct_p10": round(float(np.percentile(sides, 10)), 3) if sides else None,
                "n_classes": len({r["cls"] for r in rows}),
            })
            print(f"[{name}] {v.name}: {nframes} frame, {len(rows)} phát hiện", flush=True)

    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    (args.out / "detections.json").write_text(json.dumps(all_rows, ensure_ascii=False))
    print(f"\nđã ghi {args.out}/summary.json và detections.json")


if __name__ == "__main__":
    main()
