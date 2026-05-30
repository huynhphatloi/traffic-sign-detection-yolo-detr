"""Merge per-run metrics into the comparison table + accuracy-vs-speed chart (sections 15.4, 23).

Reads results/metrics/*.json. Accuracy files are <tag>.json; speed files are <tag>_speed.json.
They are joined on <tag>, the Efficiency Score (= mAP@0.5 x FPS) is computed, and the result
is written as results/metrics/comparison.csv plus an accuracy-vs-FPS scatter plot.

Run: python -m src.evaluation.compare_models --metrics-dir results/metrics --out results/plots
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_rows(metrics_dir: Path) -> list[dict]:
    acc: dict[str, dict] = {}
    speed: dict[str, dict] = {}
    for f in sorted(metrics_dir.glob("*.json")):
        if f.name == "comparison.json":
            continue
        data = json.loads(f.read_text())
        if f.stem.endswith("_speed"):
            speed[f.stem[: -len("_speed")]] = data
        else:
            acc[f.stem] = data

    rows = []
    for tag in sorted(set(acc) | set(speed)):
        a = acc.get(tag, {})
        s = speed.get(tag, {})
        map50 = a.get("map50")
        fps = s.get("fps")
        eff = round(map50 * fps, 3) if (map50 is not None and fps is not None) else None
        rows.append({
            "tag": tag,
            "model": a.get("model") or s.get("model"),
            "map50": map50,
            "map50_95": a.get("map50_95"),
            "precision": a.get("precision"),
            "recall": a.get("recall"),
            "fps": fps,
            "latency_ms": s.get("latency_ms"),
            "model_size_mb": s.get("model_size_mb"),
            "efficiency_score": eff,
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics-dir", type=Path, default=Path("results/metrics"))
    ap.add_argument("--out", type=Path, default=Path("results/plots"))
    args = ap.parse_args()

    import pandas as pd

    rows = load_rows(args.metrics_dir)
    if not rows:
        print(f"[compare] no metrics found in {args.metrics_dir}; run evaluate_* first.")
        return

    df = pd.DataFrame(rows)
    csv_path = args.metrics_dir / "comparison.csv"
    df.to_csv(csv_path, index=False)
    print(f"[compare] wrote {csv_path}\n")
    print(df.to_string(index=False))

    # Accuracy-vs-speed scatter (only rows that have both).
    plot_df = df.dropna(subset=["map50", "fps"])
    if not plot_df.empty:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        args.out.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(figsize=(8, 6))
        for model_kind, sub in plot_df.groupby("model"):
            ax.scatter(sub["fps"], sub["map50"], s=80, label=model_kind)
            for _, r in sub.iterrows():
                ax.annotate(r["tag"], (r["fps"], r["map50"]),
                            textcoords="offset points", xytext=(6, 4), fontsize=8)
        ax.set_xlabel("FPS (higher = faster)")
        ax.set_ylabel("mAP@0.5 (higher = more accurate)")
        ax.set_title("Accuracy vs Speed: YOLO vs DETR across strategies")
        ax.grid(True, alpha=0.3)
        ax.legend()
        plot_path = args.out / "accuracy_vs_speed.png"
        fig.tight_layout()
        fig.savefig(plot_path, dpi=150)
        print(f"\n[compare] wrote {plot_path}")


if __name__ == "__main__":
    main()
