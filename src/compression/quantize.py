"""Xuất ONNX và lượng tử hoá INT8 sau huấn luyện.

Mô-đun xuất ra HAI bản: FP32 và INT8. Bản FP32 tồn tại để **cô lập biến số** — nếu
chỉ so INT8 với mô hình PyTorch gốc, phần chênh lệch sẽ trộn lẫn hai nguyên nhân là
đổi môi trường thực thi và lượng tử hoá. Có mốc FP32 ở giữa mới quy được phần chênh
lệch giữa hai bản ONNX về đúng tác động của lượng tử hoá.

Hàm `inspect_onnx` đếm số nút lượng tử hoá trong đồ thị. Tỉ lệ giữa `DequantizeLinear`
và `QuantizeLinear` cho biết mô hình phải giải lượng tử hoá về float bao nhiêu lần để
tính rồi lượng tử hoá lại — đây là lý do cấu trúc giải thích vì sao INT8 có thể CHẬM
hơn FP32 khi môi trường thực thi thiếu nhân tính toán số nguyên được tối ưu.

CLI:
    python -m src.compression.quantize --weights weights/yolo26/student_kd_yolo26n.pt
    python -m src.compression.quantize --inspect weights/yolo26/student_kd_int8.onnx
"""
from __future__ import annotations

import argparse
import collections
from pathlib import Path

from src.utils.paths import W_KD, WEIGHTS_YOLO26, ensure_dir

N_CALIB = 300  # số ảnh dùng để hiệu chuẩn dải giá trị kích hoạt
IMGSZ = 640

_QUANT_OPS = {
    "QuantizeLinear", "DequantizeLinear",
    "QLinearConv", "QLinearMatMul", "DynamicQuantizeLinear",
}


def export(weights: Path = W_KD, imgsz: int = IMGSZ, int8: bool = True,
           data: Path | None = None, out_root: Path = WEIGHTS_YOLO26) -> dict[str, Path]:
    """Xuất sang ONNX FP32 và (tuỳ chọn) INT8. Trả về {'fp32': path, 'int8': path}."""
    from ultralytics import YOLO

    from src.utils.paths import resolved_data_yaml
    data = Path(data) if data is not None else resolved_data_yaml()
    ensure_dir(out_root)
    stem = Path(weights).stem
    out: dict[str, Path] = {}

    print("[quantize] ▶ [1/2] ONNX FP32 ...", flush=True)
    p = YOLO(str(weights)).export(format="onnx", imgsz=imgsz, opset=19, simplify=True)
    dst = out_root / f"{stem}_fp32.onnx"
    Path(p).replace(dst)
    out["fp32"] = dst

    if int8:
        print("[quantize] ▶ [2/2] ONNX INT8 ...", flush=True)
        p = YOLO(str(weights)).export(
            format="onnx", imgsz=imgsz, opset=19, simplify=True,
            int8=True, data=str(data), fraction=1.0,
        )
        dst = out_root / f"{stem}_int8.onnx"
        Path(p).replace(dst)
        out["int8"] = dst

    for k, v in out.items():
        print(f"[quantize]   {k}: {v}  ({v.stat().st_size / 1024**2:.2f} MiB)")
    return out


def inspect_onnx(path: Path) -> dict:
    """Kiểm tra đồ thị ONNX: hợp lệ, đếm nút lượng tử hoá, chạy thử một lượt."""
    import numpy as np
    import onnx
    import onnxruntime as ort

    m = onnx.load(str(path))
    onnx.checker.check_model(m)
    ops = collections.Counter(n.op_type for n in m.graph.node)
    n_quant = sum(v for k, v in ops.items() if k in _QUANT_OPS)

    sess = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    shape = [d if isinstance(d, int) else 1 for d in inp.shape]
    y = sess.run(None, {inp.name: np.random.rand(*shape).astype(np.float32)})

    return {
        "file": str(path),
        "size_mib": round(path.stat().st_size / 1024**2, 2),
        "graph_valid": True,
        "n_nodes": len(m.graph.node),
        "n_quant_nodes": n_quant,
        "quantize_linear": ops.get("QuantizeLinear", 0),
        "dequantize_linear": ops.get("DequantizeLinear", 0),
        "opset": {o.domain or "ai.onnx": o.version for o in m.opset_import},
        "input_shape": list(inp.shape),
        "output_shapes": [list(a.shape) for a in y],
        "runtime_ok": True,
        "has_nan": bool(any(np.isnan(a).any() for a in y)),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Xuất ONNX và lượng tử hoá INT8.")
    ap.add_argument("--weights", type=Path, default=W_KD)
    ap.add_argument("--imgsz", type=int, default=IMGSZ)
    ap.add_argument("--no-int8", action="store_true")
    ap.add_argument("--inspect", type=Path, default=None,
                    help="chỉ kiểm tra một tệp .onnx có sẵn, không xuất lại")
    args = ap.parse_args()

    if args.inspect:
        import json
        print(json.dumps(inspect_onnx(args.inspect), indent=2, ensure_ascii=False))
        return

    out = export(args.weights, args.imgsz, int8=not args.no_int8)
    for k, v in out.items():
        info = inspect_onnx(v)
        print(f"[quantize] {k}: {info['n_quant_nodes']} nút lượng tử hoá, "
              f"NaN={info['has_nan']}, runtime OK")


if __name__ == "__main__":
    main()
