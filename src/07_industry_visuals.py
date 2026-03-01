"""
07_industry_visuals.py

Industry-Grade Visualization Suite
ADAS Severity Amplification Framework

Author: TEJAS MANJUNATH
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE_DIR = os.path.join(BASE_DIR, "outputs", "tables")
FIG_DIR = os.path.join(BASE_DIR, "outputs", "figures")

os.makedirs(FIG_DIR, exist_ok=True)

# ==========================================================
# LOAD LATEST ODDS RATIO FILE
# ==========================================================

files = [f for f in os.listdir(TABLE_DIR) if f.startswith("odds_ratios_")]
latest_file = sorted(files)[-1]

print("Loading:", latest_file)

odds = pd.read_csv(os.path.join(TABLE_DIR, latest_file), index_col=0)

# Remove intercept
odds = odds[~odds.index.str.contains("Intercept")]

# Keep strong & meaningful drivers only
odds = odds[odds["p_value"] < 0.01]

# Sort descending
odds = odds.sort_values("odds_ratio", ascending=False)

# Take top 10
odds = odds.head(10)

# ==========================================================
# CLEAN LABELS
# ==========================================================

def clean_label(x):
    x = x.replace("C(mechanism_clean)[T.", "")
    x = x.replace("C(state_clean)[T.", "")
    x = x.replace("C(hour_bin)[T.", "")
    x = x.replace("]", "")
    x = x.replace("_", " ")
    return x

odds["label"] = odds.index.map(clean_label)

# Reverse for horizontal plotting
odds = odds.iloc[::-1]

# ==========================================================
# STYLE SETTINGS
# ==========================================================

plt.figure(figsize=(10, 6))

sns.set_style("whitegrid")
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12
})

# ==========================================================
# PLOT (Industry + Professional CI Version)
# ==========================================================

plt.figure(figsize=(10, 5.6))
sns.set_style("white")

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12
})

# ----------------------------------------------------------
# Color logic (refined tones)
# ----------------------------------------------------------

colors = [
    "#A93226" if x > 3 else "#2E6F95"
    for x in odds["odds_ratio"]
]

bars = plt.barh(
    odds["label"],
    odds["odds_ratio"],
    color=colors,
    edgecolor="none",
    zorder=2
)

# ----------------------------------------------------------
# Confidence Intervals (clean scientific styling)
# ----------------------------------------------------------

plt.errorbar(
    odds["odds_ratio"],
    odds["label"],
    xerr=[
        odds["odds_ratio"] - odds["lower_ci"],
        odds["upper_ci"] - odds["odds_ratio"]
    ],
    fmt="none",
    ecolor="#222222",
    elinewidth=1.1,
    capsize=4,
    capthick=1.1,
    zorder=1
)

# ----------------------------------------------------------
# Dynamic label placement (proportional padding)
# ----------------------------------------------------------

x_padding = odds["odds_ratio"].max() * 0.06

for i, v in enumerate(odds["odds_ratio"]):
    plt.text(
        v - x_padding,
        i,
        f"{v:.2f}×",
        va="center",
        ha="right",
        color="white",
        fontsize=10,
        fontweight="semibold",
        zorder=3
    )

# ----------------------------------------------------------
# Reference Line (OR = 1)
# ----------------------------------------------------------

plt.axvline(
    1,
    linestyle="--",
    color="#666666",
    linewidth=1.2,
    alpha=0.5
)

# ----------------------------------------------------------
# Axis Limits (adaptive spacing)
# ----------------------------------------------------------

plt.xlim(0, odds["upper_ci"].max() + odds["upper_ci"].max() * 0.08)

sns.despine()

plt.xlabel("Severity Amplification (Odds Ratio)")
plt.title(
    "Crash Mechanisms with Highest Severity Amplification\n"
    "German National Accident Dataset (≈1.5M cases)",
    weight="semibold"
)

plt.tight_layout()

output_path = os.path.join(FIG_DIR, "01_severity_amplification_publication.png")
plt.savefig(output_path, dpi=600, bbox_inches="tight")
plt.close()

print("Saved:", output_path)