"""
13_gap_analysis.py

Euro NCAP Gap Mapping
Takes compound top-10 scenarios and maps protocol coverage + gap score.

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
    "compound_top10_for_gap_analysis.csv"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TABLE_DIR = os.path.join(OUTPUT_DIR, "tables")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

os.makedirs(TABLE_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================

print("Loading top 10 compound scenarios...")
df = pd.read_csv(
    os.path.join(TABLE_DIR, "compound_top10_for_gap_analysis.csv"),
    encoding="cp1252"
)
# Ensure scenario_name column exists
if "scenario_name" not in df.columns:
    raise ValueError("scenario_name column not found in input file.")

# ==========================================================
# MANUAL COVERAGE MAP (From Step 2 Review)
# ==========================================================

coverage_map = {
    "Collision - oncoming vehicle + Motorcycle + HeavyVehicle": ("Partial", 1),
    "Collision - vehicle vs pedestrian + HeavyVehicle + Pedestrian": ("Partial", 1),
    "Leaving carriageway (left) + Motorcycle": ("Not Covered", 2),
    "Leaving carriageway (left) + Night + Motorcycle": ("Not Covered", 2),
    "Leaving carriageway (right) + Motorcycle": ("Not Covered", 2),
    "Collision - oncoming vehicle + Motorcycle": ("Covered", 0),
    "Collision - oncoming vehicle + Night + HeavyVehicle": ("Partial", 1),
    "Collision - oncoming vehicle + HeavyVehicle": ("Partial", 1),
    "Collision - oncoming vehicle + Night + Motorcycle": ("Covered", 0),
    "Leaving carriageway (right) + Night + Motorcycle": ("Not Covered", 2),
}

# Map coverage + gap score
df["Euro NCAP Coverage"] = df["scenario_name"].map(
    lambda x: coverage_map.get(x, ("Unknown", None))[0]
)

df["gap_score"] = df["scenario_name"].map(
    lambda x: coverage_map.get(x, ("Unknown", None))[1]
)

# Safety check
if df["gap_score"].isnull().any():
    print("Warning: Some scenarios missing coverage mapping.")

# ==========================================================
# SORT FOR CLARITY
# ==========================================================

df = df.sort_values("severity_rate", ascending=False)
plt.gca().invert_yaxis()
# ==========================================================
# SAVE CLEAN TABLE
# ==========================================================

output_table_path = os.path.join(
    TABLE_DIR,
    "gap_analysis_table.csv"
)

df.to_csv(output_table_path, index=False)
print(f"Saved gap analysis table to: {output_table_path}")

# ==========================================================
# VISUALISATION
# ==========================================================

print("Generating visualization...")

df = df.sort_values("severity_rate", ascending=False)

color_map = {
    "Covered": "#2ca02c",
    "Partial": "#ff7f0e",
    "Not Covered": "#d62728",
    "Unknown": "#7f7f7f"
}

colors = df["Euro NCAP Coverage"].map(color_map)

plt.figure(figsize=(11,7))

plt.barh(
    df["scenario_name"],
    df["severity_rate"],
    color=colors
)

# Flip so highest severity appears at top
plt.gca().invert_yaxis()

# Severity labels
for i, v in enumerate(df["severity_rate"]):
    plt.text(v + 0.01, i, f"{v:.2f}", va='center')

plt.xlabel("Severe Injury Rate")

plt.title(
    "High-Severity Real-World Crash Scenarios vs Euro NCAP Test Coverage",
    fontsize=14
)

# Legend
from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor="#2ca02c", label="Covered"),
    Patch(facecolor="#ff7f0e", label="Partially Covered"),
    Patch(facecolor="#d62728", label="Not Covered")
]

plt.legend(handles=legend_elements, title="Euro NCAP Coverage")

plt.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()

fig_path = os.path.join(FIG_DIR, "06_gap_visualisation.png")
plt.savefig(fig_path, dpi=300)
plt.close()

print(f"Saved visualization to: {fig_path}")

print("\nGap analysis complete.")