"""Real-time traffic-sign detection app (Streamlit) for the self-driving demo.

Run from the project root so `src` is importable:
    streamlit run src/app/app.py

Inputs: webcam / uploaded video.
Shows: boxes, labels, confidence, live FPS, per-class detection stats, a driving-style
       warning panel (current detections + FPS + model + threshold), screenshot,
       optional annotated-video save, and a low-FPS warning.
"""
from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

# Make `src` importable when launched via `streamlit run src/app/app.py`.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cv2  # noqa: E402
import streamlit as st  # noqa: E402

from src.app.inference import YoloDetector, draw_detections, draw_hud  # noqa: E402
from src.app.statistics import DetectionStats  # noqa: E402


def list_checkpoints() -> list[str]:
    weights_dir = ROOT / "weights" / "yolo"
    found = sorted(str(p) for p in weights_dir.rglob("best.pt"))
    return found or ["yolov8s.pt"]  # fall back to a pretrained model for a first demo


@st.cache_resource(show_spinner=True)
def load_detector(weights: str, imgsz: int) -> YoloDetector:
    return YoloDetector(weights, imgsz=imgsz)


def warning_panel_text(dets, fps: float, weights: str, conf: float) -> str:
    """Driving-style summary: current per-class detection counts + FPS + model + threshold."""
    from collections import Counter

    counts = Counter(d.cls_name for d in dets)
    lines = ["Detected:"]
    if counts:
        lines += [f"- {name}: {n}" for name, n in counts.most_common()]
    else:
        lines.append("- (none)")
    lines += [
        "",
        f"Current FPS: {fps:.1f}",
        f"Model: {Path(weights).parent.name if weights.endswith('.pt') else weights}",
        f"Confidence threshold: {conf:.2f}",
    ]
    return "\n".join(lines)


def main() -> None:
    st.set_page_config(page_title="Traffic Sign Detector", layout="wide")
    st.title("Real-Time Traffic Sign Detector — Self-Driving Demo")

    with st.sidebar:
        st.header("Model")
        weights = st.selectbox("Checkpoint", list_checkpoints())
        imgsz = st.select_slider("Inference size", [320, 416, 512, 640, 768], value=640)
        conf = st.slider("Confidence threshold", 0.05, 0.95, 0.25, 0.05)
        frame_skip = st.slider("Frame skip (speed)", 0, 5, 0)

        st.header("Input")
        mode = st.radio("Source", ["Upload video", "Webcam"])
        uploaded = st.file_uploader("Video file", ["mp4", "mov", "avi", "mkv"]) \
            if mode == "Upload video" else None
        save_output = st.checkbox("Save annotated video", value=False)
        run = st.button("Start", type="primary")
        stop = st.button("Stop")

    detector = load_detector(weights, imgsz)
    col_video, col_panel = st.columns([3, 1])
    frame_slot = col_video.empty()
    col_panel.subheader("Warning panel")
    warn_slot = col_panel.empty()
    stats_slot = st.sidebar.empty()
    shot_slot = st.empty()
    stats = DetectionStats()

    if "running" not in st.session_state:
        st.session_state.running = False
    if run:
        st.session_state.running = True
    if stop:
        st.session_state.running = False

    # Resolve the video source.
    if mode == "Webcam":
        source = 0
    elif uploaded is not None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix)
        tmp.write(uploaded.read())
        source = tmp.name
    else:
        source = None

    writer = None
    if st.session_state.running and source is not None:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            st.error(f"Could not open source: {source}")
            st.session_state.running = False
            return

        if save_output:
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out_path = ROOT / "results" / "real_world_outputs" / "app_output.mp4"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"),
                                     cap.get(cv2.CAP_PROP_FPS) or 25.0, (w, h))

        last = time.perf_counter()
        last_frame = None
        while st.session_state.running:
            ok, frame = cap.read()
            if not ok:
                break
            for _ in range(frame_skip):
                cap.read()

            dets = detector.detect(frame, conf=conf)
            now = time.perf_counter()
            fps = 1.0 / max(1e-6, now - last)
            last = now

            stats.update(dets)
            frame = draw_detections(frame, dets)
            frame = draw_hud(frame, fps, len(dets))
            last_frame = frame
            frame_slot.image(frame, channels="BGR", use_container_width=True)
            warn_slot.code(warning_panel_text(dets, fps, weights, conf))
            stats_slot.dataframe(stats.as_table(), use_container_width=True)
            if writer is not None:
                writer.write(frame)

        cap.release()
        if writer is not None:
            writer.release()
            st.sidebar.success(f"Saved: {out_path}")
        if last_frame is not None and shot_slot.button("Save screenshot"):
            shot_path = ROOT / "results" / "predictions" / f"screenshot_{int(time.time())}.png"
            shot_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(shot_path), last_frame)
            st.success(f"Screenshot saved: {shot_path}")
    elif st.session_state.running:
        st.warning("Choose a video file or switch to Webcam, then press Start.")


if __name__ == "__main__":
    main()
