"""Convert the YOLO-TXT dataset to COCO JSON for DETR (plan §8.6) — OWNER: Tu.

TODO (Tu): implement. For each split, read YOLO labels, denormalize boxes to absolute
[x, y, w, h] pixels (COCO convention, top-left origin), and write one JSON per split.
Expected output: data/coco/instances_{train,valid,test}.json
Reuse: src.data.inspect_dataset.{list_images,label_path_for,parse_label_file},
       src.utils.paths.{DATA_COCO,load_classes}.

This file is an intentional stub — see TODO.md.
"""
