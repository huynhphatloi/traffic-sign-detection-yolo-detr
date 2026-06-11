"""Class distribution and imbalance (plan §8.4) — OWNER: Vinh."""
from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt

from src.eda.bbox_statistics import collect_boxes
from src.utils.paths import CLASSES_YAML, RESULTS_EDA, RESULTS_TABLES, load_classes
from src.utils.plotting import save_fig

def run() -> None:
    df = collect_boxes()
    if df.empty:
        print("[class_distribution] No boxes found.")
        return

    # Load class names
    class_names = load_classes(CLASSES_YAML) if CLASSES_YAML.exists() else {}

    # Count boxes per class
    counts = df["cls"].value_counts().reset_index()
    counts.columns = ["class_id", "count"]
    
    # Add class name
    counts["class_name"] = counts["class_id"].map(lambda x: class_names.get(x, str(x)))
    
    # Calculate ratios
    max_count = counts["count"].max()
    min_count = counts["count"].min() if counts["count"].min() > 0 else 1
    imbalance_ratio = max_count / min_count
    
    counts["pct"] = (counts["count"] / counts["count"].sum() * 100).round(2)
    counts["ratio_to_max"] = (max_count / counts["count"]).round(2)

    # Sort for plotting
    counts = counts.sort_values(by="count", ascending=True) # Ascending for horizontal bar chart

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(counts["class_name"], counts["count"], color="cornflowerblue", edgecolor="black")
    ax.set_title(f"Class Distribution (Imbalance Ratio: {imbalance_ratio:.2f}x)")
    ax.set_xlabel("Number of Bounding Boxes")
    ax.set_ylabel("Class")
    save_fig(fig, RESULTS_EDA / "class_distribution.png")

    # Sort descending for CSV
    counts = counts.sort_values(by="count", ascending=False)
    
    out_csv = RESULTS_TABLES / "class_distribution.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(out_csv, index=False)

    print(f"[class_distribution] Most frequent: {counts.iloc[0]['class_name']} ({counts.iloc[0]['count']})")
    print(f"[class_distribution] Least frequent: {counts.iloc[-1]['class_name']} ({counts.iloc[-1]['count']})")
    print(f"[class_distribution] Imbalance ratio: {imbalance_ratio:.2f}x")
    print(f"[class_distribution] Generated plot in {RESULTS_EDA}")
    print(f"[class_distribution] Saved table to {out_csv}")

if __name__ == "__main__":
    run()
