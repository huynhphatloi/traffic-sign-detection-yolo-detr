"""Fine-tune DETR (facebook/detr-resnet-50) on our COCO-format data (plan section 11.2).

Reads the COCO JSON produced by src.data.convert_to_coco. Each image record carries an
`abs_path` so the dataset can load images regardless of CWD. Trains with a low backbone LR
(standard DETR recipe) and saves the model + processor to weights/detr/<name>.

DETR is slow; for previews use --epochs 10 --imgsz 480. Treat DETR as the research-
comparison track, not the deployment model (plan risk 27.2).

Example:
  python -m src.training.train_detr --coco data/processed/coco --split cardetection --name detr_baseline
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .train_yolo import AUG_PRESETS  # noqa: F401  (kept for parity; DETR aug handled below)


class CocoDetDataset:
    """Minimal COCO detection dataset for DETR's image processor."""

    def __init__(self, coco_json: Path, processor):
        import cv2  # local import

        self.cv2 = cv2
        self.processor = processor
        data = json.loads(Path(coco_json).read_text())
        self.images = {im["id"]: im for im in data["images"]}
        self.image_ids = list(self.images.keys())
        self.anns_by_img: dict[int, list] = {i: [] for i in self.image_ids}
        for a in data["annotations"]:
            self.anns_by_img[a["image_id"]].append(a)

    def __len__(self):
        return len(self.image_ids)

    def __getitem__(self, idx):
        img_id = self.image_ids[idx]
        info = self.images[img_id]
        path = info.get("abs_path") or info["file_name"]
        img = self.cv2.imread(path)
        img = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2RGB)

        annotations = [
            {"bbox": a["bbox"], "category_id": a["category_id"],
             "area": a["area"], "iscrowd": a.get("iscrowd", 0), "image_id": img_id}
            for a in self.anns_by_img[img_id]
        ]
        target = {"image_id": img_id, "annotations": annotations}
        enc = self.processor(images=img, annotations=target, return_tensors="pt")
        return {
            "pixel_values": enc["pixel_values"][0],
            "labels": enc["labels"][0],
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coco", type=Path, default=Path("data/processed/coco"))
    ap.add_argument("--split", default="cardetection", help="dataset name under --coco")
    ap.add_argument("--name", required=True)
    ap.add_argument("--checkpoint", default="facebook/detr-resnet-50")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lr-backbone", type=float, default=1e-5)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    import torch
    from torch.utils.data import DataLoader
    from transformers import DetrForObjectDetection, DetrImageProcessor

    from src.data.common import load_classes

    classes = load_classes()
    id2label = {cid: name for cid, name in classes.items()}
    label2id = {name: cid for cid, name in classes.items()}

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    processor = DetrImageProcessor.from_pretrained(args.checkpoint)
    model = DetrForObjectDetection.from_pretrained(
        args.checkpoint,
        num_labels=len(classes),
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True,  # replace the COCO-80 head with ours
    ).to(device)

    def collate(batch):
        pixel_values = [b["pixel_values"] for b in batch]
        enc = processor.pad(pixel_values, return_tensors="pt")
        return {
            "pixel_values": enc["pixel_values"],
            "pixel_mask": enc["pixel_mask"],
            "labels": [b["labels"] for b in batch],
        }

    train_ds = CocoDetDataset(args.coco / args.split / "train.json", processor)
    train_dl = DataLoader(train_ds, batch_size=args.batch, shuffle=True, collate_fn=collate)

    # Two param groups: backbone gets a smaller LR (standard DETR schedule).
    backbone = [p for n, p in model.named_parameters() if "backbone" in n and p.requires_grad]
    rest = [p for n, p in model.named_parameters() if "backbone" not in n and p.requires_grad]
    optimizer = torch.optim.AdamW(
        [{"params": rest, "lr": args.lr},
         {"params": backbone, "lr": args.lr_backbone}],
        weight_decay=args.weight_decay,
    )

    model.train()
    for epoch in range(args.epochs):
        running = 0.0
        for step, batch in enumerate(train_dl):
            pixel_values = batch["pixel_values"].to(device)
            pixel_mask = batch["pixel_mask"].to(device)
            labels = [{k: v.to(device) for k, v in t.items()} for t in batch["labels"]]
            outputs = model(pixel_values=pixel_values, pixel_mask=pixel_mask, labels=labels)
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.1)
            optimizer.step()
            running += loss.item()
        print(f"[detr] epoch {epoch + 1}/{args.epochs} loss={running / max(1, len(train_dl)):.4f}")

    dest = Path("weights/detr") / args.name
    dest.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(dest)
    processor.save_pretrained(dest)
    print(f"[detr] saved model + processor -> {dest}")


if __name__ == "__main__":
    main()
