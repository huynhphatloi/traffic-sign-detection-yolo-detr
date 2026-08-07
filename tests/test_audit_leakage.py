"""Kiểm thử mô-đun kiểm toán rò rỉ dữ liệu.

Chạy trên dữ liệu tổng hợp dựng tại chỗ, không cần GPU và không cần bộ dữ liệu thật.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.data import audit_leakage as al

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


def test_source_name_strips_roboflow_suffix():
    """Roboflow thêm hậu tố băm; hai bản sao cùng ảnh nguồn phải quy về một tên."""
    a = Path("road545_png.rf.02614a36cb366d36c8c23deca405fc02.jpg")
    b = Path("road545_png.rf.ffffffffffffffffffffffffffffffff.jpg")
    assert al.source_name(a) == al.source_name(b) == "road545_png"


def test_source_name_leaves_plain_names_alone():
    assert al.source_name(Path("000235_jpg.jpg")) == "000235_jpg"
    assert al.source_name(Path("FisheyeCamera_1_00037.png")) == "FisheyeCamera_1_00037"


def _write(path: Path, seed: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    cv2.imwrite(str(path), (rng.random((16, 16, 3)) * 255).astype("uint8"))


@pytest.fixture
def leaky_root(tmp_path: Path) -> Path:
    """Bộ dữ liệu tổng hợp có đúng MỘT ảnh kiểm tra rò rỉ từ tập huấn luyện."""
    root = tmp_path / "ds"
    _write(root / "train" / "images" / "roadA_png.rf.aaaaaa.jpg", 1)
    _write(root / "train" / "images" / "roadB_png.rf.bbbbbb.jpg", 2)
    _write(root / "valid" / "images" / "roadC_png.rf.cccccc.jpg", 3)
    # rò rỉ: cùng ảnh nguồn roadA, hậu tố khác
    _write(root / "test" / "images" / "roadA_png.rf.dddddd.jpg", 1)
    _write(root / "test" / "images" / "roadD_png.rf.eeeeee.jpg", 4)
    return root


def test_detects_leak_between_train_and_test(leaky_root: Path):
    rep = al.audit(leaky_root, with_hash=False)
    assert rep["leaked_test_images"] == 1
    assert rep["test_images"] == 2
    assert rep["clean_test_images"] == 1
    assert rep["leak_ratio"] == pytest.approx(0.5)
    assert rep["leaked_test_files"] == ["roadA_png.rf.dddddd.jpg"]


def test_byte_identical_counted_independently_of_filename(leaky_root: Path):
    """Đếm trùng byte phải băm TOÀN BỘ ảnh, không chỉ trong nhóm cùng tên nguồn.

    Regression: bản đầu chỉ băm trong nhóm cùng tên nguồn nên báo thiếu (90 thay vì
    101 trên bộ dữ liệu thật).
    """
    rep = al.audit(leaky_root, with_hash=True)
    # roadA xuất hiện ở train và test với cùng nội dung -> đúng một nhóm băm trải 2 tập
    assert rep["byte_identical_groups"] == 1


def test_clean_dataset_reports_no_leak(tmp_path: Path):
    root = tmp_path / "clean"
    for i, split in enumerate(("train", "valid", "test")):
        _write(root / split / "images" / f"img{i}_png.rf.{i:06x}.jpg", 10 + i)
    rep = al.audit(root, with_hash=True)
    assert rep["cross_split_groups"] == 0
    assert rep["leaked_test_images"] == 0
    assert rep["byte_identical_groups"] == 0


def test_summary_mentions_inflation_only_when_leaking(leaky_root: Path, tmp_path: Path):
    assert "THỔI PHỒNG" in al.summarize(al.audit(leaky_root, with_hash=False))
    root = tmp_path / "c2"
    _write(root / "train" / "images" / "a.jpg", 1)
    _write(root / "test" / "images" / "b.jpg", 2)
    assert "THỔI PHỒNG" not in al.summarize(al.audit(root, with_hash=False))
