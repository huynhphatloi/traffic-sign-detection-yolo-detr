"""Lightweight DETR baseline training (plan §8.6) — OWNER: Tu.

TODO (Tu): implement. Fine-tune `facebook/detr-resnet-50` on the COCO export (batch 2,
~5-10 epochs, pretrained, ignore_mismatched_sizes for the 15-class head). Needs a GPU (Colab).
Expected output: weights/detr/detr_baseline/  (model + image processor)
Reuse: transformers DetrForObjectDetection/DetrImageProcessor, torchvision CocoDetection,
       src.data.convert_to_coco output, src.utils.paths.

This file is an intentional stub — see TODO.md.
"""
