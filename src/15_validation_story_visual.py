"""
15_validation_story_visual.py

Final project summary visual:
Real-world crash severity vs Euro NCAP protocol coverage.

Author: TEJAS MANJUNATH
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_PATH = os.path.join(
    BASE_DIR,
    "outputs",
    "tables",
    "gap_analysis_table.csv"
)

FIG_DIR = os.path.join(BASE_DIR, "outputs", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================

print("Loading gap analysis table...")

df = pd.read_csv(INPUT_PATH, encoding="cp1252")

df = df.sort_values("severity_rate", ascending=False).reset_index(drop=True)

# ==========================================================
# COLOR MAP
# ==========================================================

color_map = {
    "Covered": "#2ca02c",        # Green
    "Partial": "#ff7f0e",        # Orange
    "Not Covered": "#d62728"     # Red
}

colors = df["Euro NCAP Coverage"].map(color_map)

# ==========================================================
# BASELINE
# ==========================================================

BASELINE = 0.1856

# ==========================================================
# PLOT
# ==========================================================

plt.figure(figsize=(13,7))

bars = plt.barh(
    df["scenario_name"],
    df["severity_rate"],
    color=colors
)

plt.gca().invert_yaxis()

# Baseline vertical line
plt.axvline(
    BASELINE,
    linestyle="--",
    color="black",
    linewidth=1.5
)

plt.text(
    BASELINE - 0.01,
    len(df)-0.4,
    "National severe injury baseline: 18.56%",
    fontsize=9
)

# Percentage labels
for i, v in enumerate(df["severity_rate"]):
    plt.text(
        v + 0.01,
        i,
        f"{v*100:.1f}%",
        va="center",
        fontsize=10
    )

# Labels
plt.xlabel("Severe Injury Rate")

# Main title
plt.title(
    "Real-World High-Severity Scenarios vs Euro NCAP AEB Protocol Coverage",
    fontsize=15,
    pad=35,
    weight="bold"
)

# Subtitle
plt.figtext(
    0.5,
    0.93,
    "Colour indicates Euro NCAP test protocol representation · German National Accident Dataset (1.53M records)",
    ha="center",
    fontsize=10,
    color="gray"
)

# Legend
from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor="#d62728", label="Not Covered"),
    Patch(facecolor="#ff7f0e", label="Partially Covered"),
    Patch(facecolor="#2ca02c", label="Covered")
]

plt.legend(
    handles=legend_elements,
    title="Euro NCAP Coverage",
    loc="lower right"
)

plt.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()

# ==========================================================
# SAVE
# ==========================================================

OUTPUT_PATH = os.path.join(
    FIG_DIR,
    "08_validation_story_visual.png"
)

plt.savefig(OUTPUT_PATH, dpi=300)
plt.close()

print(f"Validation story visual saved to: {OUTPUT_PATH}")