"""
10_compound_amplification.py

Compound Severity Amplification Analysis
Identifies structural multi-factor risk escalation

Author: TEJAS MANJUNATH
"""

import os
import pandas as pd
import numpy as np

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "Data", "processed", "cleaned_accidents.pkl")

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TABLE_DIR = os.path.join(OUTPUT_DIR, "tables")

os.makedirs(TABLE_DIR, exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================

print("Loading dataset...")
df = pd.read_pickle(DATA_PATH)

baseline_rate = df["is_high_severity"].mean()
print("Baseline high severity rate:", round(baseline_rate, 4))

# ==========================================================
# SELECT CORE FACTORS
# ==========================================================

columns = [
    "is_high_severity",
    "accident_mechanism",
    "is_night",
    "pedestrian_involved",
    "motorcycle_involved",
    "heavy_vehicle_involved"
]

df = df[columns].copy()

# Clean mechanism (top 10 only)
top_mechs = df["accident_mechanism"].value_counts().nlargest(10).index
df["mechanism_clean"] = df["accident_mechanism"].where(
    df["accident_mechanism"].isin(top_mechs),
    "Other"
)

# ==========================================================
# COMPOUND GROUP ANALYSIS
# ==========================================================

group_cols = [
    "mechanism_clean",
    "is_night",
    "motorcycle_involved",
    "heavy_vehicle_involved",
    "pedestrian_involved"
]

compound = df.groupby(group_cols).agg(
    total_accidents=("is_high_severity", "count"),
    severe_cases=("is_high_severity", "sum")
).reset_index()

compound["severity_rate"] = compound["severe_cases"] / compound["total_accidents"]
compound["excess_over_baseline"] = compound["severity_rate"] - baseline_rate
compound["relative_amplification"] = compound["severity_rate"] / baseline_rate

# Remove low exposure noise
compound = compound[compound["total_accidents"] > 500]

compound = compound.sort_values("relative_amplification", ascending=False)

# Save table
output_path = os.path.join(TABLE_DIR, "compound_amplification_analysis.csv")
compound.to_csv(output_path, index=False)

print("\nTop 15 Compound Amplification Structures:")
print(compound.head(15))

print("\nSaved compound amplification table to:", output_path)