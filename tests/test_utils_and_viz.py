"""Kiểm thử path helper, bộ vẽ chú thích và đăng ký mô hình.

Hai test của compare_models đã được gỡ: mô-đun đó thuộc giai đoạn giữa kỳ và đã
chuyển sang mid-work/. Thay vào đó là test cho đăng ký MODELS của cuối kỳ."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.utils import paths as P
from src.data import visualize_annotations as viz


# ── paths ─────────────────────────────────────────────────────────────────────
def test_split_dir_val_alias(tmp_path: Path):
    assert P.split_dir("val", tmp_path).name == "valid"
    assert P.split_dir("valid", tmp_path).name == "valid"
    assert P.split_dir("train", tmp_path).name == "train"


def test_load_classes_dict_form(classes_yaml: Path):
    assert P.load_classes(classes_yaml) == {0: "Green Light", 1: "Red Light", 2: "Stop"}


def test_load_classes_list_form(tmp_path: Path):
    p = tmp_path / "list.yaml"
    p.write_text("names: [a, b, c]\n")
    assert P.load_classes(p) == {0: "a", 1: "b", 2: "c"}


def test_ensure_dir_creates(tmp_path: Path):
    target = tmp_path / "a" / "b" / "c"
    assert not target.exists()
    P.ensure_dir(target)
    assert target.is_dir()


# ── visualize_annotations.draw_boxes ───────────────────────────────────────────
def test_draw_boxes_marks_pixels_and_preserves_shape():
    img = np.zeros((100, 100, 3), dtype="uint8")
    before = img.copy()
    out = viz.draw_boxes(img, [(0, 0.5, 0.5, 0.4, 0.4)], {0: "Stop"})
    assert out.shape == before.shape
    # something was drawn (non-zero pixels now exist)
    assert out.sum() > 0


def test_draw_boxes_unknown_class_falls_back_to_id():
    img = np.zeros((50, 50, 3), dtype="uint8")
    # should not raise even when the class id is absent from the name map
    viz.draw_boxes(img, [(7, 0.5, 0.5, 0.2, 0.2)], {})


# ── đăng ký mô hình ─────────────────────────────────────────────────────────


# ── đăng ký mô hình của giai đoạn cuối kỳ ────────────────────────────────────
def test_models_registry_has_four_configs():
    """MODELS phải khai báo đủ bốn cấu hình mà báo cáo trình bày."""
    assert set(P.MODELS) == {"teacher", "student_baseline", "student_kd", "student_kd_int8"}


def test_models_registry_points_into_yolo26_dir():
    for name, path in P.MODELS.items():
        assert path.parent == P.WEIGHTS_YOLO26, f"{name} không nằm trong weights/yolo26"


def test_no_midterm_weight_constants_remain():
    """Regression: hằng số trọng số YOLOv8/DETR phải biến mất khỏi paths.

    Chúng thuộc giai đoạn giữa kỳ, đã chuyển sang mid-work/. Nếu còn sót, một
    mô-đun nào đó vẫn đang trỏ vào cây thư mục cũ.
    """
    assert not hasattr(P, "WEIGHTS_YOLO")
    assert not hasattr(P, "WEIGHTS_DETR")
