"""Chưng cất tri thức: mô hình thầy lớn dạy mô hình học trò nhỏ.

Thiết kế then chốt của mô-đun này là **đối chứng đúng nghĩa**: hàm `train_student`
được gọi HAI lần với mọi tham số giống hệt nhau, chỉ khác `teacher=None` hay không.
Nhờ vậy chênh lệch quan sát được quy về đúng biến số cần khảo sát.

Một yếu tố gây nhiễu chưa kiểm soát được, cần nêu rõ: nhánh chưng cất phải nạp đồng
thời cả hai mô hình vào bộ nhớ card đồ hoạ nên buộc dùng kích thước lô nhỏ hơn. Vì
kích thước lô ảnh hưởng tới chất lượng ước lượng gradient, kết luận đúng mực là
"trong cấu hình cụ thể này chưng cất không mang lại lợi ích", KHÔNG phải "chưng cất
có hại". Muốn kết luận chắc chắn phải dùng tích luỹ gradient để hai nhánh có cùng
kích thước lô hiệu dụng.

CLI:
    python -m src.compression.distill --stage teacher
    python -m src.compression.distill --stage baseline
    python -m src.compression.distill --stage kd
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from src.utils.paths import WEIGHTS_YOLO26, ensure_dir, resolved_data_yaml
from src.utils.seeding import DEFAULT_SEED

TEACHER_MODEL = "yolo26s.pt"
STUDENT_MODEL = "yolo26n.pt"
EPOCHS = 50
PATIENCE = 12
IMGSZ = 640
DIS_WEIGHT = 6.0  # giá trị mặc định của thư viện, CHƯA được quét thử

# Kích thước lô cho từng giai đoạn. Nhánh KD nhỏ hơn vì phải nạp cả hai mô hình.
BATCH = {"teacher": 16, "baseline": 24, "kd": 8}

OUT_NAME = {
    "teacher": "teacher_yolo26s.pt",
    "baseline": "student_baseline_yolo26n.pt",
    "kd": "student_kd_yolo26n.pt",
}


def train_stage(stage: str, data: Path | None = None, epochs: int = EPOCHS,
                imgsz: int = IMGSZ, device: str | None = None,
                dis: float = DIS_WEIGHT, out_root: Path = WEIGHTS_YOLO26):
    """Huấn luyện một trong ba giai đoạn; trả về (results, đường dẫn best.pt)."""
    from ultralytics import YOLO

    from src.utils.seeding import seed_everything
    seed_everything(DEFAULT_SEED)

    if stage not in BATCH:
        raise ValueError(f"stage phải là một trong {list(BATCH)}, nhận '{stage}'")

    data = Path(data) if data is not None else resolved_data_yaml()
    base = TEACHER_MODEL if stage == "teacher" else STUDENT_MODEL
    kwargs = dict(
        data=str(data), epochs=epochs, imgsz=imgsz, batch=BATCH[stage],
        patience=PATIENCE, seed=DEFAULT_SEED, device=device,
        name=f"yolo26_{stage}", cos_lr=True, verbose=True,
    )

    if stage == "kd":
        teacher = out_root / OUT_NAME["teacher"]
        if not teacher.exists():
            raise FileNotFoundError(
                f"chưa có mô hình thầy tại {teacher}. Chạy `--stage teacher` trước."
            )
        # Chính hai tham số này bật cơ chế chưng cất. Khi bật, nhật ký huấn luyện có
        # thêm cột `train/dis_loss` — dùng để xác minh cơ chế thực sự chạy.
        kwargs.update(distill_model=str(teacher), dis=dis)

    print(f"[distill] ▶ {stage}: {base}, {epochs} chu kỳ, lô {BATCH[stage]}"
          + (f", dis={dis}" if stage == "kd" else ""), flush=True)

    net = YOLO(base)
    results = net.train(**kwargs)

    run_dir = Path(getattr(results, "save_dir", net.trainer.save_dir))
    src_best = run_dir / "weights" / "best.pt"
    dst = ensure_dir(out_root) / OUT_NAME[stage]
    if src_best.exists():
        shutil.copy2(src_best, dst)
        print(f"[distill] ✔ lưu {dst}")
    return results, dst


def verify_distillation(run_dir: Path) -> dict:
    """Xác minh chưng cất ĐÃ THỰC SỰ chạy, đọc từ results.csv của lần huấn luyện.

    Nếu không có bước này thì một kết quả âm không phân biệt được với trường hợp cơ
    chế chưng cất chưa hề được kích hoạt — khi đó ta chỉ đang so hai lần huấn luyện
    thông thường với kích thước lô khác nhau.
    """
    import pandas as pd

    csv = Path(run_dir) / "results.csv"
    if not csv.exists():
        return {"enabled": False, "reason": f"không thấy {csv}"}
    df = pd.read_csv(csv)
    df.columns = [c.strip() for c in df.columns]
    col = next((c for c in df.columns if "dis_loss" in c), None)
    if col is None:
        return {"enabled": False, "reason": "không có cột dis_loss trong results.csv"}
    first, last = float(df[col].iloc[0]), float(df[col].iloc[-1])
    return {
        "enabled": True, "column": col,
        "first_epoch": first, "last_epoch": last,
        "converged": last < first,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Huấn luyện thầy / trò đối chứng / trò chưng cất.")
    ap.add_argument("--stage", required=True, choices=list(BATCH))
    ap.add_argument("--data", type=Path, default=None)
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--imgsz", type=int, default=IMGSZ)
    ap.add_argument("--dis", type=float, default=DIS_WEIGHT)
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    results, dst = train_stage(args.stage, args.data, args.epochs,
                               args.imgsz, args.device, args.dis)
    if args.stage == "kd":
        info = verify_distillation(getattr(results, "save_dir", ""))
        print(f"[distill] xác minh chưng cất: {info}")


if __name__ == "__main__":
    main()
