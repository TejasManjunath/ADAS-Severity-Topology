"""
07_validation_framework.py

ADAS Validation Strategy Layer
Risk × Exposure Prioritization Framework

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
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TABLE_DIR = os.path.join(OUTPUT_DIR, "tables")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

os.makedirs(FIG_DIR, exist_ok=True)

# ==========================================================
# LOAD SCENARIO TABLE
# ==========================================================

scenario_path = os.path.join(TABLE_DIR, "adas_priority_index.csv")
scenario = pd.read_csv(scenario_path)

print("Loaded scenario table:", scenario.shape)

# ==========================================================
# DERIVE RISK & EXPOSURE METRICS
# ==========================================================

baseline_rate = scenario["severity_rate"].mean()

scenario["exposure_log"] = np.log1p(scenario["total_accidents"])
scenario["risk_score"] = scenario["severity_rate"] - baseline_rate

risk_threshold = scenario["risk_score"].quantile(0.75)
exposure_threshold = scenario["exposure_log"].quantile(0.75)

def assign_tier(row):
    if row["risk_score"] >= risk_threshold and row["exposure_log"] >= exposure_threshold:
        return "Tier 1 - Critical"
    elif row["risk_score"] >= scenario["risk_score"].median():
        return "Tier 2 - High"
    else:
        return "Tier 3 - Standard"

scenario["validation_tier"] = scenario.apply(assign_tier, axis=1)

# ==========================================================
# SAVE UPDATED TABLE
# ==========================================================

tiered_output = os.path.join(TABLE_DIR, "adas_validation_tiers.csv")
scenario.to_csv(tiered_output, index=False)

print("Saved tiered scenario table:", tiered_output)
# ==========================================================
# STRATEGIC RISK × EXPOSURE FRAMEWORK
# ==========================================================

plt.figure(figsize=(8.5, 6.5))

# Clean scientific style
sns.set_style("white")
plt.grid(True, linestyle='-', linewidth=0.6, alpha=0.18)

# ----------------------------------------------------------
# Bubble size scaling (stronger contrast, same logic)
# ----------------------------------------------------------

size_scale = 1000

normalized_size = (
    (scenario["AVPI"] - scenario["AVPI"].min()) /
    (scenario["AVPI"].max() - scenario["AVPI"].min())
)

scenario["bubble_size"] = 120 + normalized_size * size_scale

tier_colors = {
    "Tier 1 - Critical": "#B03A2E",
    "Tier 2 - High": "#D68910",
    "Tier 3 - Standard": "#2471A3"
}

tier_alpha = {
    "Tier 1 - Critical": 0.95,
    "Tier 2 - High": 0.70,
    "Tier 3 - Standard": 0.45
}

tier_linewidth = {
    "Tier 1 - Critical": 1.8,
    "Tier 2 - High": 1.0,
    "Tier 3 - Standard": 0.8
}

# Plot in controlled order (background → foreground)
for tier in ["Tier 3 - Standard", "Tier 2 - High", "Tier 1 - Critical"]:

    group = scenario[scenario["validation_tier"] == tier]

    plt.scatter(
        group["exposure_log"],
        group["risk_score"],
        s=group["bubble_size"],
        alpha=tier_alpha[tier],
        color=tier_colors[tier],
        edgecolors="white",
        linewidth=tier_linewidth[tier],
        label=tier,
        zorder=3 if tier == "Tier 1 - Critical" else 2
    )

# ----------------------------------------------------------
# Quadrant lines (intentional styling)
# ----------------------------------------------------------

plt.axhline(
    risk_threshold,
    linestyle="--",
    color="black",
    linewidth=1.3,
    alpha=0.65
)

plt.axvline(
    exposure_threshold,
    linestyle="--",
    color="black",
    linewidth=1.3,
    alpha=0.65
)

# ----------------------------------------------------------
# Labels & title
# ----------------------------------------------------------

plt.xlabel("Exposure (log accident frequency)", fontsize=12)
plt.ylabel("Excess Severity Risk", fontsize=12)

plt.title(
    "ADAS Validation Strategy: Risk × Exposure Prioritization",
    fontsize=14,
    weight="semibold"
)

plt.tick_params(axis='both', labelsize=11)

# Clean legend (same placement as your refined version)
plt.legend(
    frameon=True,
    facecolor="white",
    framealpha=0.95,
    edgecolor="#CCCCCC",
    fontsize=11,
    loc="upper right"
)

plt.tight_layout()

figure_path = os.path.join(FIG_DIR, "02_adas_validation_quadrant_publication.png")
plt.savefig(figure_path, dpi=600, bbox_inches="tight")
plt.close()

print("Saved publication-grade quadrant plot:", figure_path)