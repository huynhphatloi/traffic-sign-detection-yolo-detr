"""Ràng giao ước giữa tệp chú thích COCO và mã sinh dự đoán.

Bối cảnh: `src/data/convert_to_coco.py` giữ nguyên chỉ số lớp của YOLO nên `category_id`
chạy từ 0, trong khi quy ước COCO gốc chạy từ 1. Một phiên bản trước của
`src/evaluation/coco_eval.py` cộng thêm 1 theo quy ước gốc, làm lệch toàn bộ nhãn đi một
bậc. Hậu quả rất dễ bị bỏ sót vì hộp bao vẫn đúng chỗ: mAP@0,5 tụt từ 0,9014 xuống 0,0160
trong khi mAP bỏ qua lớp vẫn giữ 0,9403.

Các kiểm thử ở đây chạy trên dữ liệu tổng hợp, không cần mô hình, không cần GPU, và không
cần bộ dữ liệu thật — nên chúng chạy được ở mọi môi trường.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.data.convert_to_coco import convert
from src.evaluation import coco_eval as ce

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

pytest.importorskip("pycocotools")

N_CLASSES = 4
IMG = 64


def _synth_gt(n_images: int = 6) -> dict:
    """Tệp COCO tối giản: mỗi ảnh một hộp, lớp chạy vòng qua N_CLASSES."""
    images, anns = [], []
    for i in range(1, n_images + 1):
        images.append({"id": i, "file_name": f"{i}.jpg", "width": IMG, "height": IMG})
        anns.append({
            "id": i, "image_id": i, "category_id": (i - 1) % N_CLASSES,
            "bbox": [8.0, 8.0, 20.0, 20.0], "area": 400.0, "iscrowd": 0,
        })
    return {
        "categories": [{"id": c, "name": f"c{c}"} for c in range(N_CLASSES)],
        "images": images, "annotations": anns,
    }


def _dets_from_gt(gt: dict, offset: int = 0) -> list[dict]:
    """Dự đoán hoàn hảo về vị trí; `offset` mô phỏng đúng lỗi lệch nhãn lớp."""
    return [{
        "image_id": a["image_id"],
        "category_id": a["category_id"] + offset,
        "bbox": list(a["bbox"]),
        "score": 0.9,
    } for a in gt["annotations"]]


def test_offset_zero_gives_perfect_map():
    """Không lệch nhãn thì dự đoán trùng khít hộp thật phải cho mAP bằng 1."""
    gt = _synth_gt()
    r = ce.coco_eval(gt, _dets_from_gt(gt, ce.CATEGORY_ID_OFFSET))
    assert r is not None
    assert r["map50"] == pytest.approx(1.0, abs=1e-6)


def test_shifted_labels_collapse_map_but_not_localization():
    """Chữ ký của lỗi: mAP sụp gần không NHƯNG mAP bỏ qua lớp vẫn hoàn hảo.

    Đây chính là dấu hiệu đã quan sát được trên bộ dữ liệu thật. Kiểm thử ràng cả hai vế
    để phân biệt lỗi lệch nhãn với một mô hình dự đoán kém thật sự — mô hình kém thì cả
    hai chỉ số cùng thấp.
    """
    gt = _synth_gt()
    shifted = _dets_from_gt(gt, ce.CATEGORY_ID_OFFSET + 1)

    r = ce.coco_eval(gt, shifted)
    assert r is not None
    assert r["map50"] < 0.5, "lệch nhãn lớp lẽ ra phải làm mAP sụp"

    ca = ce.class_agnostic_eval(gt, shifted)
    assert ca is not None
    assert ca["map50"] == pytest.approx(1.0, abs=1e-6), (
        "vị trí hộp không đổi nên mAP bỏ qua lớp phải giữ nguyên"
    )


@pytest.mark.skipif(cv2 is None, reason="cần OpenCV để ghi ảnh tổng hợp")
def test_converter_emits_zero_based_category_ids(tmp_path, monkeypatch):
    """Chốt đầu kia của giao ước: bộ chuyển đổi phải phát `category_id` bắt đầu từ 0.

    Nếu ai đó đổi `convert_to_coco` sang quy ước COCO gốc mà quên đổi
    `CATEGORY_ID_OFFSET`, kiểm thử này đỏ trước khi lỗi kịp lan tới báo cáo.
    """
    root, out = tmp_path / "ds", tmp_path / "coco"
    rng = np.random.default_rng(0)
    for split in ("train", "valid", "test"):
        (root / split / "images").mkdir(parents=True)
        (root / split / "labels").mkdir(parents=True)
        cv2.imwrite(str(root / split / "images" / "a.jpg"),
                    (rng.random((IMG, IMG, 3)) * 255).astype("uint8"))
        # lớp 0 — chính là lớp sẽ biến mất nếu quy ước bị đổi sang 1-based
        (root / split / "labels" / "a.txt").write_text("0 0.5 0.5 0.3 0.3\n")

    monkeypatch.setattr("src.data.convert_to_coco.load_classes",
                        lambda: {c: f"c{c}" for c in range(N_CLASSES)})
    convert(root=root, out_dir=out)

    import json
    coco = json.loads((out / "instances_test.json").read_text())
    assert min(c["id"] for c in coco["categories"]) == ce.CATEGORY_ID_OFFSET
    assert coco["annotations"][0]["category_id"] == ce.CATEGORY_ID_OFFSET
