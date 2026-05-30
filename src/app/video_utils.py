"""Video I/O helpers for the app and the offline real-world video tests (section 22)."""
from __future__ import annotations

import time
from pathlib import Path

import cv2


def frame_iter(source, frame_skip: int = 0):
    """Yield (frame_bgr, fps) from a webcam index or a video file path.

    frame_skip>0 drops that many frames between yields — a cheap real-time speedup
    (plan risk 27.4). `fps` is a smoothed processing rate, not the source fps.
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"could not open video source: {source!r}")
    last = time.perf_counter()
    smoothed = 0.0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            for _ in range(frame_skip):
                cap.read()
            now = time.perf_counter()
            inst = 1.0 / max(1e-6, now - last)
            smoothed = inst if smoothed == 0 else 0.9 * smoothed + 0.1 * inst
            last = now
            yield frame, smoothed
    finally:
        cap.release()


def annotate_video(source: str, detector, out_path: str, conf: float = 0.25,
                   frame_skip: int = 0) -> str:
    """Run the detector over a whole video file and write an annotated MP4.

    Used by notebook 06 / the real-world VN test set to produce demo clips.
    """
    from .inference import draw_detections, draw_hud

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"could not open {source}")
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), src_fps, (w, h))

    last = time.perf_counter()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            for _ in range(frame_skip):
                cap.read()
            dets = detector.detect(frame, conf=conf)
            now = time.perf_counter()
            fps = 1.0 / max(1e-6, now - last)
            last = now
            frame = draw_detections(frame, dets)
            frame = draw_hud(frame, fps, len(dets))
            writer.write(frame)
    finally:
        cap.release()
        writer.release()
    return out_path
