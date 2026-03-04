"""
14_srpi_ranking.py

Strategic Risk Priority Index (SRPI)
Ranks compound scenarios for ADAS validation priority.

Author: TEJAS MANJUNATH
"""

import os
import pandas as pd
import numpy as np
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

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TABLE_DIR = os.path.join(OUTPUT_DIR, "tables")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

os.makedirs(TABLE_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================

print("Loading gap analysis table...")

df = pd.read_csv(
    os.path.join(TABLE_DIR, "gap_analysis_table.csv"),
    encoding="cp1252"
)

# ==========================================================
# SRPI CALCULATION
# ==========================================================

# Log exposure
df["log_exposure"] = np.log(df["total_accidents"])

# SRPI formula
df["SRPI"] = (
    df["severity_rate"] * 0.5 +
    df["gap_score"] * 0.3 +
    df["log_exposure"] * 0.2
)

# Rank descending
df = df.sort_values("SRPI", ascending=False)

# ==========================================================
# SAVE RANKED TABLE
# ==========================================================

output_path = os.path.join(TABLE_DIR, "srpi_ranking.csv")
df.to_csv(output_path, index=False)

print(f"Saved SRPI ranking to: {output_path}")

# ==========================================================
# VISUALISATION
# ==========================================================

# Select top scenarios for visual clarity
top_df = df.head(10)

plt.figure(figsize=(10, 7))

bars = plt.barh(
    top_df["scenario_name"],
    top_df["SRPI"],
    color="steelblue"
)

plt.xlabel("Strategic Risk Priority Index (SRPI)")
plt.title("ADAS Scenario Validation Priority Ranking")

# Flip axis so highest SRPI appears at top
plt.gca().invert_yaxis()

# Add grid for readability
plt.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()

for i, v in enumerate(top_df["SRPI"]):
    plt.text(v + 0.02, i, f"{v:.2f}", va="center")
    
fig_path = os.path.join(FIG_DIR, "srpi_ranking.png")
plt.savefig(fig_path, dpi=300)
plt.close()

print(f"Saved SRPI figure to: {fig_path}")