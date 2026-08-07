"""Kiểm toán rò rỉ dữ liệu giữa các tập.

Bản xuất Roboflow thêm một hậu tố băm ngẫu nhiên vào tên tệp
(`road545_png.rf.02614a36....jpg`), nên hai bản sao của CÙNG một ảnh nguồn có tên
khác nhau và không bị phát hiện nếu chỉ so tên đầy đủ. Mô-đun này đối chiếu ở hai
mức:

  1. tên ảnh nguồn sau khi bóc hậu tố `.rf.<hash>`,
  2. băm nội dung tệp, để xác định các cặp trùng byte hoàn toàn.

Rò rỉ giữa tập huấn luyện và tập kiểm tra làm chỉ số bị thổi phồng một cách âm thầm:
mô hình đã nhìn thấy đúng những ảnh đó lúc huấn luyện, nên phần dự đoán trên chúng
thiên về ghi nhớ hơn là khái quát hoá.

CLI:
    python -m src.data.audit_leakage
Output:
    results/metrics/data_leakage.json   (có danh sách tệp rò rỉ, dùng bởi coco_eval)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from src.data.inspect_dataset import list_images
from src.utils.paths import DATA_PROCESSED, RESULTS_METRICS, SPLITS, ensure_dir

# Hậu tố Roboflow: <tên gốc>.rf.<hash 32 ký tự>.<đuôi>
_RF_SUFFIX = re.compile(r"\.rf\.[0-9a-f]{6,}$", re.I)


def source_name(path: Path) -> str:
    """Tên ảnh nguồn sau khi bóc hậu tố ngẫu nhiên của Roboflow."""
    return _RF_SUFFIX.sub("", path.stem)


def file_digest(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while blk := f.read(chunk):
            h.update(blk)
    return h.hexdigest()


def audit(root: Path = DATA_PROCESSED, with_hash: bool = True) -> dict:
    by_source: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    counts: dict[str, int] = {}
    for split in SPLITS:
        imgs = list_images(split, root)
        counts[split] = len(imgs)
        for p in imgs:
            by_source[source_name(p)].append((split, p))

    # Nhóm ảnh nguồn xuất hiện ở nhiều hơn một tập
    cross = {src: items for src, items in by_source.items()
             if len({sp for sp, _ in items}) > 1}

    # Đếm trùng byte độc lập với tên tệp: băm TOÀN BỘ ảnh rồi đếm các nhóm-băm trải
    # nhiều hơn một tập. Cách này rộng hơn việc chỉ băm trong các nhóm cùng tên nguồn
    # — nó bắt được cả những ảnh giống hệt nhau nhưng mang tên nguồn khác nhau, vốn
    # bị heuristic tên tệp bỏ sót.
    byte_dup = 0
    if with_hash:
        by_digest: dict[str, set[str]] = defaultdict(set)
        for split in SPLITS:
            for p in list_images(split, root):
                by_digest[file_digest(p)].add(split)
        byte_dup = sum(1 for splits in by_digest.values() if len(splits) > 1)

    leaked_test = sorted({
        p.name for items in cross.values() for sp, p in items
        if sp == "test" and any(s == "train" for s, _ in items)
    })

    n_test = counts.get("test", 0)
    return {
        "images_per_split": counts,
        "cross_split_groups": len(cross),
        "byte_identical_groups": byte_dup,
        "leaked_test_images": len(leaked_test),
        "test_images": n_test,
        "leak_ratio": round(len(leaked_test) / n_test, 4) if n_test else None,
        "clean_test_images": n_test - len(leaked_test),
        "leaked_test_files": leaked_test,
    }


def summarize(rep: dict) -> str:
    lines = [
        "-" * 62,
        "RÒ RỈ GIỮA CÁC TẬP (theo tên ảnh nguồn)",
        "-" * 62,
        f"  Nhóm ảnh nguồn ở >1 tập          : {rep['cross_split_groups']}",
        f"  Trong đó trùng BYTE hoàn toàn    : {rep['byte_identical_groups']}",
        f"  Ảnh KIỂM TRA trùng với TẬP TRAIN : {rep['leaked_test_images']} / "
        f"{rep['test_images']}  ({(rep['leak_ratio'] or 0) * 100:.1f}%)",
        f"  Tập kiểm tra SẠCH còn lại        : {rep['clean_test_images']} ảnh",
    ]
    if rep["leaked_test_images"]:
        lines += ["", "!  Kết quả trên TOÀN tập kiểm tra sẽ bị THỔI PHỒNG.",
                  "!  Dùng `coco_eval --clean-only` để đo trên phần sạch."]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Kiểm toán rò rỉ dữ liệu giữa các tập.")
    ap.add_argument("--root", type=Path, default=DATA_PROCESSED)
    ap.add_argument("--no-hash", action="store_true", help="bỏ qua bước băm nội dung (nhanh hơn)")
    ap.add_argument("--out", type=Path, default=RESULTS_METRICS / "data_leakage.json")
    args = ap.parse_args()

    rep = audit(args.root, with_hash=not args.no_hash)
    print(summarize(rep))
    ensure_dir(args.out.parent)
    args.out.write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
