"""Streamlit demo for traffic-sign detection on webcam, video, and images."""
from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import pandas as pd
import streamlit as st
from PIL import Image

try:
    import av
    from streamlit_webrtc import RTCConfiguration, VideoProcessorBase, WebRtcMode, webrtc_streamer
except ImportError:
    av = None
    RTCConfiguration = None
    VideoProcessorBase = object
    WebRtcMode = None
    webrtc_streamer = None


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEIGHTS = REPO_ROOT / "weights" / "yolo" / "yolo_baseline" / "best.pt"
YOLO_METRICS = REPO_ROOT / "results" / "metrics" / "yolo_baseline.json"
OUTPUT_DIR = REPO_ROOT / "app" / "outputs"

DETECTION_COLUMNS = ["class", "confidence", "x1", "y1", "x2", "y2"]


@st.cache_resource(show_spinner="Loading YOLO model...")
def load_yolo(weights_path: str):
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "tsd-matplotlib"))

    from ultralytics import YOLO

    return YOLO(weights_path)


def load_metrics(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def check_model_ready() -> None:
    if not DEFAULT_WEIGHTS.exists():
        st.error(f"Missing YOLO weights: {DEFAULT_WEIGHTS}")
        st.stop()


def result_rows(result: Any) -> list[dict]:
    rows = []
    names = result.names
    if result.boxes is None:
        return rows

    for box in result.boxes:
        cls_id = int(box.cls.item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        rows.append(
            {
                "class": names.get(cls_id, str(cls_id)),
                "confidence": round(float(box.conf.item()), 3),
                "x1": round(x1, 1),
                "y1": round(y1, 1),
                "x2": round(x2, 1),
                "y2": round(y2, 1),
            }
        )
    return rows


def detection_table(result: Any) -> pd.DataFrame:
    return pd.DataFrame(result_rows(result), columns=DETECTION_COLUMNS)


def predict_frame(frame_bgr, conf: float, iou: float, imgsz: int):
    model = load_yolo(str(DEFAULT_WEIGHTS))
    return model.predict(frame_bgr, conf=conf, iou=iou, imgsz=imgsz, verbose=False)[0]


def summarize_rows(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["class", "detections", "avg_confidence", "max_confidence"])

    df = pd.DataFrame(rows)
    summary = (
        df.groupby("class", as_index=False)
        .agg(
            detections=("class", "size"),
            avg_confidence=("confidence", "mean"),
            max_confidence=("confidence", "max"),
        )
        .sort_values(["detections", "max_confidence"], ascending=False)
    )
    summary["avg_confidence"] = summary["avg_confidence"].round(3)
    summary["max_confidence"] = summary["max_confidence"].round(3)
    return summary


class TrafficSignVideoProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        self.conf = 0.25
        self.iou = 0.70
        self.imgsz = 640
        self.duration = 10
        self.max_inference_fps = 8
        self.started_at = time.monotonic()
        self.last_inference_at = 0.0
        self.last_annotated = None
        self.lock = threading.Lock()
        self.frame_count = 0
        self.processed_frames = 0
        self.detected_rows: list[dict] = []
        self.class_counter: Counter[str] = Counter()

    def configure(self, conf: float, iou: float, imgsz: int, duration: int, max_inference_fps: int) -> None:
        with self.lock:
            self.conf = conf
            self.iou = iou
            self.imgsz = imgsz
            self.duration = duration
            self.max_inference_fps = max_inference_fps

    def reset(self) -> None:
        with self.lock:
            self.started_at = time.monotonic()
            self.last_inference_at = 0.0
            self.last_annotated = None
            self.frame_count = 0
            self.processed_frames = 0
            self.detected_rows = []
            self.class_counter = Counter()

    def snapshot(self) -> dict:
        with self.lock:
            elapsed = time.monotonic() - self.started_at
            return {
                "elapsed": elapsed,
                "duration": self.duration,
                "frame_count": self.frame_count,
                "processed_frames": self.processed_frames,
                "detections": sum(self.class_counter.values()),
                "class_counter": dict(self.class_counter),
                "rows": list(self.detected_rows),
                "complete": elapsed >= self.duration,
            }

    def recv(self, frame):
        frame_bgr = frame.to_ndarray(format="bgr24")
        now = time.monotonic()

        with self.lock:
            self.frame_count += 1
            elapsed = now - self.started_at
            should_detect = elapsed <= self.duration and (
                now - self.last_inference_at >= 1.0 / max(self.max_inference_fps, 1)
            )
            conf = self.conf
            iou = self.iou
            imgsz = self.imgsz

        annotated = self.last_annotated if self.last_annotated is not None else frame_bgr

        if should_detect:
            result = predict_frame(frame_bgr, conf=conf, iou=iou, imgsz=imgsz)
            annotated = result.plot()
            rows = result_rows(result)

            with self.lock:
                self.last_inference_at = now
                self.last_annotated = annotated
                self.processed_frames += 1
                self.detected_rows.extend(rows)
                self.class_counter.update(row["class"] for row in rows)

        with self.lock:
            remaining = max(0.0, self.duration - (time.monotonic() - self.started_at))
            complete = remaining <= 0.0

        label = "complete" if complete else f"{remaining:0.1f}s"
        color = (0, 180, 255) if complete else (0, 255, 0)
        cv2.putText(annotated, label, (16, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)
        return av.VideoFrame.from_ndarray(annotated, format="bgr24")


def sidebar_controls(metrics: dict) -> tuple[float, float, int, int, int]:
    with st.sidebar:
        st.subheader("Model")
        st.code(str(DEFAULT_WEIGHTS.relative_to(REPO_ROOT)))
        conf = st.slider("Confidence", 0.05, 0.95, 0.25, 0.05)
        iou = st.slider("IoU", 0.10, 0.90, 0.70, 0.05)
        imgsz = st.select_slider("Image size", options=[320, 416, 512, 640, 768, 960], value=640)
        duration = st.slider("Session duration", 10, 15, 10, 1)
        inference_fps = st.slider("Inference FPS cap", 1, 15, 8, 1)

        if metrics:
            st.subheader("Test metrics")
            st.metric("mAP50", f"{metrics.get('map50', 0):.3f}")
            st.metric("mAP50-95", f"{metrics.get('map50_95', 0):.3f}")
            st.metric("FPS", f"{metrics.get('fps', 0):.1f}")

    return conf, iou, imgsz, duration, inference_fps


def render_webcam_tab(conf: float, iou: float, imgsz: int, duration: int, inference_fps: int) -> None:
    if webrtc_streamer is None:
        st.error("Missing webcam dependencies. Install with: pip install streamlit-webrtc av")
        return

    rtc_config = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    ctx = webrtc_streamer(
        key="traffic-sign-webcam",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_config,
        video_processor_factory=TrafficSignVideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    if ctx.video_processor:
        ctx.video_processor.configure(conf, iou, imgsz, duration, inference_fps)
        if st.button("Reset webcam session"):
            ctx.video_processor.reset()

        stats_placeholder = st.empty()
        table_placeholder = st.empty()
        caption_placeholder = st.empty()

        while ctx.state.playing:
            stats = ctx.video_processor.snapshot()
            elapsed = min(stats["elapsed"], stats["duration"])
            processed_fps = stats["processed_frames"] / max(elapsed, 0.01)
            top_classes = ", ".join(
                f"{name} ({count})" for name, count in Counter(stats["class_counter"]).most_common(3)
            )

            stats_placeholder.metric("Session", f"{elapsed:0.1f}s / {stats['duration']}s")
            cols = table_placeholder.columns(3)
            cols[0].metric("Processed frames", stats["processed_frames"])
            cols[1].metric("Avg inference FPS", f"{processed_fps:0.1f}")
            cols[2].metric("Detections", stats["detections"])

            if top_classes:
                caption_placeholder.caption(f"Top classes: {top_classes}")
            else:
                caption_placeholder.empty()

            time.sleep(0.5)
            if stats["complete"]:
                break

        if ctx.video_processor:
            rows = ctx.video_processor.snapshot()["rows"]
            summary = summarize_rows(rows)
            if not summary.empty:
                st.dataframe(summary, hide_index=True, width="stretch")


def process_video_file(uploaded_file, conf: float, iou: float, imgsz: int, max_seconds: int) -> tuple[Path, pd.DataFrame, dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(uploaded_file.name).suffix or ".mp4"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        input_path = Path(tmp.name)

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError("Cannot read the uploaded video. Try MP4/H.264.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    max_frames = int(max_seconds * fps)

    output_path = OUTPUT_DIR / f"annotated_{int(time.time())}.mp4"
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    all_rows: list[dict] = []
    processed = 0
    progress = st.progress(0)

    while processed < max_frames:
        ok, frame_bgr = cap.read()
        if not ok:
            break

        result = predict_frame(frame_bgr, conf=conf, iou=iou, imgsz=imgsz)
        annotated = result.plot()
        writer.write(annotated)
        all_rows.extend(result_rows(result))
        processed += 1
        progress.progress(min(processed / max(max_frames, 1), 1.0))

    cap.release()
    writer.release()
    input_path.unlink(missing_ok=True)
    progress.empty()

    stats = {
        "processed_frames": processed,
        "source_fps": round(fps, 2),
        "duration_seconds": round(processed / max(fps, 1), 2),
        "detections": len(all_rows),
    }
    return output_path, summarize_rows(all_rows), stats


def render_video_tab(conf: float, iou: float, imgsz: int, duration: int) -> None:
    uploaded_video = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_video is None:
        st.info("Upload a short traffic-scene video to detect signs frame by frame.")
        return

    if st.button("Process video"):
        with st.spinner("Running YOLO on video frames..."):
            output_path, summary, stats = process_video_file(uploaded_video, conf, iou, imgsz, duration)

        cols = st.columns(4)
        cols[0].metric("Frames", stats["processed_frames"])
        cols[1].metric("Source FPS", stats["source_fps"])
        cols[2].metric("Seconds", stats["duration_seconds"])
        cols[3].metric("Detections", stats["detections"])

        if summary.empty:
            st.warning("No traffic signs detected in this video segment.")
        else:
            st.dataframe(summary, hide_index=True, width="stretch")

        st.video(str(output_path))
        st.download_button(
            "Download annotated video",
            output_path.read_bytes(),
            file_name=output_path.name,
            mime="video/mp4",
        )


def render_image_tab(conf: float, iou: float, imgsz: int) -> None:
    camera_image = st.camera_input("Camera snapshot")
    uploaded_image = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"])
    image_source = camera_image or uploaded_image

    if image_source is None:
        st.info("Capture a camera image or upload a traffic-scene image to run single-frame detection.")
        return

    image = Image.open(image_source).convert("RGB")
    with st.spinner("Detecting traffic signs..."):
        result = load_yolo(str(DEFAULT_WEIGHTS)).predict(image, conf=conf, iou=iou, imgsz=imgsz, verbose=False)[0]
        table = detection_table(result)
        annotated = result.plot()

    left, right = st.columns([1.4, 1])
    with left:
        st.image(annotated, caption="Detections", channels="BGR", width="stretch")
    with right:
        st.metric("Detected signs", len(table))
        if table.empty:
            st.warning("No signs detected at the current confidence threshold.")
        else:
            st.dataframe(table, hide_index=True, width="stretch")


def main() -> None:
    st.set_page_config(page_title="Traffic Sign Detector", layout="wide")
    st.title("Traffic Sign Detector")

    check_model_ready()
    metrics = load_metrics(YOLO_METRICS)
    conf, iou, imgsz, duration, inference_fps = sidebar_controls(metrics)

    webcam_tab, video_tab, image_tab = st.tabs(["Webcam realtime", "Video file", "Image snapshot"])
    with webcam_tab:
        render_webcam_tab(conf, iou, imgsz, duration, inference_fps)
    with video_tab:
        render_video_tab(conf, iou, imgsz, duration)
    with image_tab:
        render_image_tab(conf, iou, imgsz)


if __name__ == "__main__":
    main()
