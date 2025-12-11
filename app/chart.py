# app/chart.py

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional

STATIC = Path(__file__).resolve().parent.parent / "static"
STATIC.mkdir(parents=True, exist_ok=True)

TABLE_HEADER_BLUE = "#4A90E2"

def generate_chart(total_income: float, total_expense: float, out_path: Optional[str] = None) -> str:
    labels = ["Income", "Expense"]
    values = [float(total_income or 0.0), float(total_expense or 0.0)]

    plt.figure(figsize=(5, 4))

    # Rounded, smooth bars
    bars = plt.bar(
        labels,
        values,
        color=TABLE_HEADER_BLUE,
        edgecolor="#2c3e50",
        linewidth=1,
    )

    # Value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + (height * 0.02),
            f"{height:,.0f}",
            ha="center",
            fontsize=10,
        )

    # Clean modern styling
    plt.title("Income vs Expense", fontsize=14, fontweight="bold")
    plt.ylabel("Amount", fontsize=10)

    plt.grid(axis="y", linestyle="--", alpha=0.3)

    # Remove top + right borders for clean look
    ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    out = out_path or str(STATIC / "chart.png")
    plt.savefig(out, dpi=140)
    plt.close()
    return out
