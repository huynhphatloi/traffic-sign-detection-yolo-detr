"""Bar charts from the merged comparison.csv (plan section 23 result tables).

Produces grouped bars of mAP@0.5 / mAP@0.5:0.95 per run and an efficiency-score bar.

Run: python -m src.visualization.plot_results --csv results/metrics/comparison.csv --out results/plots
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=Path("results/metrics/comparison.csv"))
    ap.add_argument("--out", type=Path, default=Path("results/plots"))
    args = ap.parse_args()

    if not args.csv.exists():
        raise SystemExit(f"{args.csv} not found; run src.evaluation.compare_models first.")
    df = pd.read_csv(args.csv)
    args.out.mkdir(parents=True, exist_ok=True)

    # mAP grouped bars
    acc = df.dropna(subset=["map50"])
    if not acc.empty:
        x = np.arange(len(acc))
        fig, ax = plt.subplots(figsize=(max(8, len(acc) * 1.2), 5))
        ax.bar(x - 0.2, acc["map50"], 0.4, label="mAP@0.5")
        if acc["map50_95"].notna().any():
            ax.bar(x + 0.2, acc["map50_95"].fillna(0), 0.4, label="mAP@0.5:0.95")
        ax.set_xticks(x); ax.set_xticklabels(acc["tag"], rotation=30, ha="right")
        ax.set_ylabel("mAP"); ax.set_title("Detection accuracy by run")
        ax.legend(); ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout(); fig.savefig(args.out / "map_by_run.png", dpi=150); plt.close(fig)

    # Efficiency score
    eff = df.dropna(subset=["efficiency_score"])
    if not eff.empty:
        fig, ax = plt.subplots(figsize=(max(8, len(eff) * 1.2), 5))
        ax.bar(eff["tag"], eff["efficiency_score"], color="#9b5cf6")
        ax.set_ylabel("mAP@0.5 x FPS"); ax.set_title("Efficiency score by run")
        plt.xticks(rotation=30, ha="right")
        fig.tight_layout(); fig.savefig(args.out / "efficiency_score.png", dpi=150); plt.close(fig)

    print(f"[plot_results] wrote charts to {args.out}")


if __name__ == "__main__":
    main()
