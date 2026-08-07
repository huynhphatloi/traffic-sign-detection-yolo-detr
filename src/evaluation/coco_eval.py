"""Đánh giá bằng pycocotools, có tách $AP$ theo nhóm kích thước vật thể.

Đây là mô-đun trung tâm của giai đoạn cuối kỳ. Lý do dùng pycocotools thay vì bộ
đánh giá của thư viện huấn luyện: nó cho $AP$ riêng cho ba nhóm nhỏ / trung bình /
lớn theo quy ước COCO (ngưỡng $32^2$ và $96^2$ điểm ảnh). Chỉ số đó trả lời được câu
hỏi mà mAP tổng không trả lời được --- khi một phép can thiệp làm mô hình kém đi,
*phần kém đó rơi vào nhóm nào*.

Dùng chung một bộ tính cho cả mô hình PyTorch lẫn ONNX cũng loại bỏ khả năng chênh
lệch đến từ hai cài đặt mAP khác nhau.

CLI:
    python -m src.evaluation.coco_eval                      # cả 4 cấu hình
    python -m src.evaluation.coco_eval --models student_kd  # một cấu hình
    python -m src.evaluation.coco_eval --clean-only         # chỉ 573 ảnh không rò rỉ
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path

from src.utils.paths import DATA_COCO, DATA_PROCESSED, MODELS, RESULTS_METRICS, ensure_dir

# Ngưỡng tin cậy khi đo gần bằng KHÔNG, có chủ ý: mAP là độ đo xếp hạng nên cần trọn
# bộ dự đoán có điểm số để dựng đầy đủ đường cong PR. Lọc trước sẽ cắt mất phần đuôi
# độ bao phủ và làm sai lệch chỉ số.
# Độ lệch giữa chỉ số lớp của Ultralytics và `category_id` trong tệp COCO của đề tài.
# `src/data/convert_to_coco.py` giữ nguyên chỉ số YOLO nên danh mục chạy từ 0, khác quy
# ước COCO gốc chạy từ 1. Đặt sai hằng số này làm mAP sụp xuống gần không trong khi mAP
# bỏ qua lớp vẫn cao — `tests/test_coco_eval_contract.py` ràng đúng trường hợp đó.
CATEGORY_ID_OFFSET = 0

CONF_EVAL = 0.001
IOU_NMS = 0.70
MAX_DET = 300
IMGSZ = 640


def _load_gt(split: str = "test", coco_dir: Path = DATA_COCO) -> dict:
    path = coco_dir / f"instances_{split}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"không thấy {path}. Chạy `python -m src.data.convert_to_coco` trước."
        )
    return json.loads(path.read_text())


def predict_all(weights: Path, gt: dict, split: str, device: str | None,
                imgsz: int = IMGSZ) -> list[dict]:
    """Chạy suy luận trên toàn bộ ảnh của split, trả về danh sách dự đoán kiểu COCO.

    Nhãn lớp được dùng NGUYÊN, không cộng thêm. Quy ước COCO gốc đánh `category_id` từ
    1, nhưng `src/data/convert_to_coco.py` của đề tài giữ nguyên chỉ số lớp YOLO nên
    bảng danh mục ở đây chạy từ 0 đến 14. Cộng 1 sẽ làm lệch toàn bộ nhãn đi một bậc:
    hộp bao vẫn đúng chỗ nhưng lớp thì sai, khiến mAP sụp xuống gần không trong khi
    $mAP$ bỏ qua lớp vẫn cao --- đúng dấu hiệu đã gặp khi lỗi này còn tồn tại.
    """
    from PIL import Image
    from ultralytics import YOLO

    model = YOLO(str(weights), task="detect")
    img_dir = DATA_PROCESSED / split / "images"
    dets: list[dict] = []
    for i, meta in enumerate(gt["images"], 1):
        if i % 100 == 0:
            print(f"[coco_eval]   {i}/{len(gt['images'])} ảnh", flush=True)
        image = Image.open(img_dir / meta["file_name"]).convert("RGB")
        r = model.predict(image, conf=CONF_EVAL, iou=IOU_NMS, max_det=MAX_DET,
                          imgsz=imgsz, device=device, verbose=False)[0]
        if r.boxes is None or len(r.boxes) == 0:
            continue
        xyxy = r.boxes.xyxy.cpu().numpy()
        conf = r.boxes.conf.cpu().numpy()
        cls = r.boxes.cls.cpu().numpy().astype(int)
        for (x1, y1, x2, y2), s, c in zip(xyxy, conf, cls):
            dets.append({
                "image_id": meta["id"],
                "category_id": int(c) + CATEGORY_ID_OFFSET,
                "bbox": [float(x1), float(y1), float(x2 - x1), float(y2 - y1)],
                "score": float(s),
            })
    return dets


def coco_eval(gt: dict, dets: list[dict], img_ids: list[int] | None = None) -> dict | None:
    """Chạy COCOeval. `img_ids=None` là toàn tập; truyền danh sách để giới hạn.

    Tham số `img_ids` chính là cách đo riêng trên tập kiểm tra SẠCH (573 ảnh không bị
    rò rỉ) mà không phải dựng lại tệp chú thích.
    """
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval

    if not dets:
        return None
    with contextlib.redirect_stdout(io.StringIO()):
        c = COCO()
        c.dataset = gt
        c.createIndex()
        e = COCOeval(c, c.loadRes(list(dets)), "bbox")
        if img_ids is not None:
            e.params.imgIds = sorted(img_ids)
        e.evaluate()
        e.accumulate()
        e.summarize()
    s = e.stats
    return {
        "map50_95": float(s[0]), "map50": float(s[1]), "map75": float(s[2]),
        "ap_small": float(s[3]), "ap_medium": float(s[4]), "ap_large": float(s[5]),
        "recall_100": float(s[8]),
    }


def class_agnostic_eval(gt: dict, dets: list[dict]) -> dict | None:
    """Gộp 15 lớp thành 1 để đo riêng khả năng ĐỊNH VỊ.

    Chênh lệch giữa chỉ số này và mAP thường cho biết mô hình đang hỏng ở khâu định vị
    hay khâu phân loại --- với bộ dữ liệu biển báo, nơi 13 lớp giới hạn tốc độ chỉ khác
    nhau ở chữ số bên trong, phân biệt đó rất có ý nghĩa.
    """
    g = json.loads(json.dumps(gt))
    for a in g["annotations"]:
        a["category_id"] = 1
    g["categories"] = [{"id": 1, "name": "sign"}]
    return coco_eval(g, [dict(d, category_id=1) for d in dets])


def clean_image_ids(gt: dict, leak_report: Path | None = None) -> list[int] | None:
    """ID của các ảnh kiểm tra KHÔNG bị rò rỉ, đọc từ báo cáo kiểm toán."""
    leak_report = leak_report or (RESULTS_METRICS / "data_leakage.json")
    if not leak_report.exists():
        return None
    leaked = set(json.loads(leak_report.read_text()).get("leaked_test_files", []))
    if not leaked:
        return None
    return [im["id"] for im in gt["images"] if im["file_name"] not in leaked]


def evaluate(name: str, weights: Path, split: str = "test",
             device: str | None = None, clean_only: bool = False) -> dict:
    gt = _load_gt(split)
    print(f"[coco_eval] ▶ {name} — {len(gt['images'])} ảnh, {len(gt['annotations'])} hộp", flush=True)
    dets = predict_all(weights, gt, split, device)

    ids = clean_image_ids(gt) if clean_only else None
    if clean_only and ids is None:
        print("[coco_eval]   ⚠ chưa có báo cáo rò rỉ — đo trên toàn tập")

    result: dict = {"model": name, "weights": str(weights), "split": split,
                    "n_images": len(ids) if ids else len(gt["images"]),
                    "subset": "clean" if ids else "full"}
    result.update(coco_eval(gt, dets, ids) or {})
    ca = class_agnostic_eval(gt, dets)
    if ca:
        result["localization_only_map50"] = ca["map50"]
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Đánh giá COCO có tách AP theo kích thước.")
    ap.add_argument("--models", nargs="*", default=list(MODELS),
                    help=f"chọn trong: {' '.join(MODELS)}")
    ap.add_argument("--split", default="test")
    ap.add_argument("--device", default=None)
    ap.add_argument("--clean-only", action="store_true",
                    help="chỉ đo trên các ảnh kiểm tra không bị rò rỉ")
    ap.add_argument("--out", type=Path, default=RESULTS_METRICS)
    args = ap.parse_args()

    ensure_dir(args.out)
    rows = []
    for name in args.models:
        if name not in MODELS:
            raise SystemExit(f"không biết cấu hình '{name}'. Chọn: {', '.join(MODELS)}")
        w = MODELS[name]
        if not w.exists():
            print(f"[coco_eval] bỏ qua {name}: không thấy {w}")
            continue
        r = evaluate(name, w, args.split, args.device, args.clean_only)
        suffix = "_clean" if args.clean_only else ""
        (args.out / f"{name}{suffix}.json").write_text(json.dumps(r, indent=2))
        rows.append(r)
        print(f"[coco_eval] ✔ {name}: mAP@0,5={r.get('map50', 0):.4f}  "
              f"AP nhỏ={r.get('ap_small', 0):.4f}  AP lớn={r.get('ap_large', 0):.4f}")

    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)[
            ["model", "subset", "n_images", "map50", "map50_95", "ap_small",
             "ap_medium", "ap_large", "localization_only_map50"]
        ]
        print("\n" + df.to_string(index=False))
        out_csv = args.out.parent / "tables" / ("coco_eval%s.csv" % ("_clean" if args.clean_only else ""))
        ensure_dir(out_csv.parent)
        df.to_csv(out_csv, index=False)
        print(f"\nwrote {out_csv}")


if __name__ == "__main__":
    main()
