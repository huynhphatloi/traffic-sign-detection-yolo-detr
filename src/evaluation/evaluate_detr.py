"""Evaluate a fine-tuned DETR model on a COCO split and save unified metrics JSON.

Uses torchmetrics MeanAveragePrecision so DETR and YOLO report comparable numbers
(mAP@0.5, mAP@0.5:0.95). Evaluate on the same test split as YOLO for a fair comparison.

Example:
  python -m src.evaluation.evaluate_detr --model weights/detr/detr_baseline \
      --coco data/processed/coco --split cardetection --tag detr_baseline
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="dir saved by train_detr (model + processor)")
    ap.add_argument("--coco", type=Path, default=Path("data/processed/coco"))
    ap.add_argument("--split", default="cardetection")
    ap.add_argument("--set", default="test", choices=["train", "val", "test"])
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--device", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--out", type=Path, default=Path("results/metrics"))
    args = ap.parse_args()

    import cv2
    import torch
    from torchmetrics.detection.mean_ap import MeanAveragePrecision
    from transformers import DetrForObjectDetection, DetrImageProcessor

    from src.data.common import load_classes

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    processor = DetrImageProcessor.from_pretrained(args.model)
    model = DetrForObjectDetection.from_pretrained(args.model).to(device).eval()

    coco = json.loads((args.coco / args.split / f"{args.set}.json").read_text())
    images = {im["id"]: im for im in coco["images"]}
    anns_by_img: dict[int, list] = {i: [] for i in images}
    for a in coco["annotations"]:
        anns_by_img[a["image_id"]].append(a)

    metric = MeanAveragePrecision(box_format="xyxy", class_metrics=True)

    with torch.no_grad():
        for img_id, info in images.items():
            path = info.get("abs_path") or info["file_name"]
            bgr = cv2.imread(path)
            if bgr is None:
                continue
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            inputs = processor(images=rgb, return_tensors="pt").to(device)
            outputs = model(**inputs)
            target_sizes = torch.tensor([[info["height"], info["width"]]]).to(device)
            post = processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=args.threshold)[0]

            preds = [{
                "boxes": post["boxes"].cpu(),
                "scores": post["scores"].cpu(),
                "labels": post["labels"].cpu(),
            }]
            gt_boxes = []
            gt_labels = []
            for a in anns_by_img[img_id]:
                x, y, w, h = a["bbox"]
                gt_boxes.append([x, y, x + w, y + h])
                gt_labels.append(a["category_id"])
            targets = [{
                "boxes": torch.tensor(gt_boxes, dtype=torch.float32).reshape(-1, 4),
                "labels": torch.tensor(gt_labels, dtype=torch.long),
            }]
            metric.update(preds, targets)

    result = metric.compute()
    classes = load_classes()
    per_class = {}
    try:
        for cid, ap in zip(result["classes"].tolist(), result["map_per_class"].tolist()):
            per_class[classes.get(int(cid), str(cid))] = float(ap)
    except Exception:
        pass

    metrics = {
        "model": "detr",
        "weights": str(args.model),
        "data": f"{args.split}/{args.set}",
        "split": args.set,
        "map50": float(result["map_50"]),
        "map50_95": float(result["map"]),
        "precision": None,  # torchmetrics mAP does not expose a single P/R scalar
        "recall": float(result.get("mar_100", float("nan"))),
        "per_class_ap50": per_class,
    }

    tag = args.tag or Path(args.model).name
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{tag}.json"
    out_file.write_text(json.dumps(metrics, indent=2))
    print(f"[eval_detr] mAP50={metrics['map50']:.4f} mAP50-95={metrics['map50_95']:.4f} -> {out_file}")


if __name__ == "__main__":
    main()
