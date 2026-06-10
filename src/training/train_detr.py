"""Lightweight DETR baseline training (plan §8.6) — OWNER: Tu.

Fine-tunes facebook/detr-resnet-50 on the COCO export.
Needs a GPU (Colab).
Output: weights/detr/detr_baseline/
"""
from __future__ import annotations

import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from transformers import DetrForObjectDetection, DetrImageProcessor

from src.utils.paths import DATA_COCO, DATA_PROCESSED, WEIGHTS_DETR, ensure_dir


class CocoDetrDataset(torch.utils.data.Dataset):
    def __init__(self, coco_json: Path, processor: DetrImageProcessor):
        self.processor = processor

        with open(coco_json) as f:
            data = json.load(f)

        self.images = {img["id"]: img for img in data["images"]}
        self.img_ids = [img["id"] for img in data["images"]]

        self.anns: dict[int, list] = {img_id: [] for img_id in self.img_ids}
        for ann in data["annotations"]:
            self.anns[ann["image_id"]].append(ann)

        split = coco_json.stem.replace("instances_", "")
        self.img_dir = DATA_PROCESSED / split / "images"

    def __len__(self) -> int:
        return len(self.img_ids)

    def __getitem__(self, idx: int):
        from PIL import Image
        img_id = self.img_ids[idx]
        meta = self.images[img_id]
        img_path = self.img_dir / meta["file_name"]
        image = Image.open(img_path).convert("RGB")

        anns = self.anns[img_id]
        boxes = [[a["bbox"][0], a["bbox"][1],
                  a["bbox"][0] + a["bbox"][2],
                  a["bbox"][1] + a["bbox"][3]] for a in anns]
        labels = [a["category_id"] for a in anns]

        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32) if boxes else torch.zeros((0, 4)),
            "class_labels": torch.tensor(labels, dtype=torch.long),
        }
        encoding = self.processor(images=image, annotations=target, return_tensors="pt")
        return {
            "pixel_values": encoding["pixel_values"].squeeze(0),
            "pixel_mask":   encoding["pixel_mask"].squeeze(0),
            "labels":       encoding["labels"][0],  # list of 1 dict → unwrap
        }


def collate_fn(batch):
    pixel_values = torch.stack([b["pixel_values"] for b in batch])
    pixel_mask   = torch.stack([b["pixel_mask"]   for b in batch])
    labels = [b["labels"] for b in batch]
    return {"pixel_values": pixel_values, "pixel_mask": pixel_mask, "labels": labels}


def train(
    epochs: int = 10,
    batch: int = 2,
    lr: float = 1e-4,
    name: str = "detr_baseline",
    coco_dir: Path = DATA_COCO,
    out_root: Path = WEIGHTS_DETR,
) -> Path:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[train_detr] device={device}, epochs={epochs}, batch={batch}")

    processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
    model = DetrForObjectDetection.from_pretrained(
        "facebook/detr-resnet-50",
        num_labels=15,
        ignore_mismatched_sizes=True,
    ).to(device)

    train_ds = CocoDetrDataset(coco_dir / "instances_train.json", processor)
    val_ds   = CocoDetrDataset(coco_dir / "instances_valid.json", processor)

    train_loader = DataLoader(train_ds, batch_size=batch, shuffle=True,
                              collate_fn=collate_fn, num_workers=2)
    val_loader   = DataLoader(val_ds,   batch_size=batch, shuffle=False,
                              collate_fn=collate_fn, num_workers=2)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    best_val_loss = float("inf")
    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        total_loss = 0.0
        for batch_data in train_loader:
            pixel_values = batch_data["pixel_values"].to(device)
            pixel_mask   = batch_data["pixel_mask"].to(device)
            labels = [{k: v.to(device) for k, v in lbl.items()}
                      for lbl in batch_data["labels"]]
            outputs = model(pixel_values=pixel_values, pixel_mask=pixel_mask, labels=labels)
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.1)
            optimizer.step()
            total_loss += loss.item()

        avg_train = total_loss / len(train_loader)

        # Validate
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_data in val_loader:
                pixel_values = batch_data["pixel_values"].to(device)
                pixel_mask   = batch_data["pixel_mask"].to(device)
                labels = [{k: v.to(device) for k, v in lbl.items()}
                          for lbl in batch_data["labels"]]
                outputs = model(pixel_values=pixel_values, pixel_mask=pixel_mask, labels=labels)
                val_loss += outputs.loss.item()

        avg_val = val_loss / len(val_loader)
        print(f"[train_detr] epoch {epoch}/{epochs}  "
              f"train_loss={avg_train:.4f}  val_loss={avg_val:.4f}")

        if avg_val < best_val_loss:
            best_val_loss = avg_val
            best_epoch = epoch

    # Save model
    out_dir = ensure_dir(out_root / name)
    model.save_pretrained(out_dir)
    processor.save_pretrained(out_dir)
    print(f"[train_detr] saved → {out_dir}  (best val_loss={best_val_loss:.4f} at epoch {best_epoch})")
    return out_dir


if __name__ == "__main__":
    train()
