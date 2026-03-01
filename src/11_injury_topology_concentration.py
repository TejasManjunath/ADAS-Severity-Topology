"""
11_injury_topology_concentration.py

Quantifies concentration of severe injury burden
across crash topologies.

Author: TEJAS MANJUNATH
"""

import os
import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "Data", "processed", "cleaned_accidents.pkl")

# ==========================================================
# LOAD DATA
# ==========================================================

print("Loading dataset...")
df = pd.read_pickle(DATA_PATH)

baseline_rate = df["is_high_severity"].mean()
total_severe = df["is_high_severity"].sum()

print("Total severe cases nationally:", total_severe)
print("Baseline severity rate:", round(baseline_rate, 4))

# ==========================================================
# MECHANISM-LEVEL SEVERE CONTRIBUTION
# ==========================================================

topology = df.groupby("accident_mechanism").agg(
    total_accidents=("is_high_severity", "count"),
    severe_cases=("is_high_severity", "sum")
).reset_index()

topology["severity_rate"] = topology["severe_cases"] / topology["total_accidents"]
topology["severe_share_%"] = (
    topology["severe_cases"] / total_severe * 100
)

topology = topology.sort_values("severe_cases", ascending=False)

# Cumulative contribution
topology["cumulative_severe_%"] = topology["severe_share_%"].cumsum()

print("\nTop 10 Crash Topologies by Severe Injury Burden:")
print(topology.head(10)[[
    "accident_mechanism",
    "severe_cases",
    "severity_rate",
    "severe_share_%",
    "cumulative_severe_%"
]])

# Save table
output_path = os.path.join(BASE_DIR, "outputs", "tables", "injury_topology_concentration.csv")
topology.to_csv(output_path, index=False)

print("\nSaved injury topology concentration table to:", output_path)