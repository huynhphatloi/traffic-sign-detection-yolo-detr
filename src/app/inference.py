"""Backend inference wrapper (M2): one model, frame in -> detections + annotated frame out.

Keeps the model behind a small Detection dataclass so the UI (app.py) never touches the
YOLO API directly. Supports a confidence threshold and optional input resize for speed
(plan section 20.2 / risk 27.4).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.data.common import load_classes

# Per-class BGR colors, reused from the annotation visualizer for consistency.
COLORS = [
    (66, 135, 245), (60, 200, 90), (40, 40, 230), (230, 180, 40),
    (200, 60, 200), (40, 200, 220), (120, 90, 250), (180, 180, 180),
]


@dataclass
class Detection:
    cls_id: int
    cls_name: str
    conf: float
    xyxy: tuple[int, int, int, int]


class YoloDetector:
    """Thin wrapper around an Ultralytics YOLO checkpoint for real-time use."""

    def __init__(self, weights: str, imgsz: int = 640, device=None, half: bool = False):
        from ultralytics import YOLO

        if not Path(weights).exists():
            raise FileNotFoundError(f"weights not found: {weights}")
        self.model = YOLO(weights)
        self.imgsz = imgsz
        self.device = device
        self.half = half
        self.classes = load_classes()

    def detect(self, frame_bgr: np.ndarray, conf: float = 0.25) -> list[Detection]:
        res = self.model.predict(
            frame_bgr, imgsz=self.imgsz, conf=conf, device=self.device,
            half=self.half, verbose=False,
        )[0]
        out: list[Detection] = []
        for box in res.boxes:
            cls_id = int(box.cls[0])
            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
            out.append(Detection(
                cls_id=cls_id,
                cls_name=self.classes.get(cls_id, str(cls_id)),
                conf=float(box.conf[0]),
                xyxy=(x1, y1, x2, y2),
            ))
        return out


def draw_detections(frame_bgr: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Return a copy of the frame with boxes + labels + confidence drawn."""
    out = frame_bgr.copy()
    for d in detections:
        x1, y1, x2, y2 = d.xyxy
        color = COLORS[d.cls_id % len(COLORS)]
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        label = f"{d.cls_name} {d.conf:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(out, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(out, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def draw_hud(frame_bgr: np.ndarray, fps: float, n_det: int, low_fps: float = 15.0) -> np.ndarray:
    """Overlay FPS + detection count; warn (red) when FPS drops below threshold."""
    color = (40, 200, 90) if fps >= low_fps else (40, 40, 230)
    text = f"FPS: {fps:5.1f}  |  detections: {n_det}"
    if fps < low_fps:
        text += "  [LOW FPS]"
    cv2.putText(frame_bgr, text, (10, 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
    return frame_bgr
