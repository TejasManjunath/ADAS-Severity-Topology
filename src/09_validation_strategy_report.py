"""
09_validation_strategy_report.py

ADAS Validation Resource Allocation Simulator
Balances:
- Data-driven AVPI weighting
- Safety-critical tier multipliers
- Engineering feasibility constraints

Author: TEJAS MANJUNATH
"""

import os
import pandas as pd
import numpy as np

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TABLE_DIR = os.path.join(OUTPUT_DIR, "tables")

scenario_path = os.path.join(TABLE_DIR, "adas_validation_tiers.csv")
scenario = pd.read_csv(scenario_path)

print("Loaded tiered scenario table:", scenario.shape)

# ==========================================================
# USER-ADJUSTABLE PARAMETERS (OEM TUNING LAYER)
# ==========================================================

TIER_MULTIPLIERS = {
    "Tier 1 - Critical": 2.0,
    "Tier 2 - High": 1.0,
    "Tier 3 - Standard": 0.5
}

MIN_ALLOCATION_FLOOR = {
    "Tier 1 - Critical": 0.30,  # minimum 30%
    "Tier 2 - High": 0.0,
    "Tier 3 - Standard": 0.05   # maintain small baseline coverage
}

MAX_ALLOCATION_CAP = {
    "Tier 1 - Critical": 0.60,
    "Tier 2 - High": 0.80,
    "Tier 3 - Standard": 0.20
}

# ==========================================================
# 1️⃣ PURE DATA-DRIVEN ALLOCATION
# ==========================================================

total_AVPI = scenario["AVPI"].sum()

scenario["pure_weight"] = scenario["AVPI"] / total_AVPI

pure_allocation = (
    scenario.groupby("validation_tier")["pure_weight"]
    .sum()
    .reset_index()
)

pure_allocation.rename(columns={"pure_weight": "pure_share"}, inplace=True)

# ==========================================================
# 2️⃣ SAFETY-WEIGHTED ALLOCATION
# ==========================================================

scenario["safety_weighted_AVPI"] = scenario.apply(
    lambda row: row["AVPI"] * TIER_MULTIPLIERS[row["validation_tier"]],
    axis=1
)

total_weighted = scenario["safety_weighted_AVPI"].sum()

scenario["safety_weight"] = scenario["safety_weighted_AVPI"] / total_weighted

safety_allocation = (
    scenario.groupby("validation_tier")["safety_weight"]
    .sum()
    .reset_index()
)

safety_allocation.rename(columns={"safety_weight": "safety_share"}, inplace=True)

# ==========================================================
# 3️⃣ ENGINEERING-CONSTRAINED ALLOCATION
# ==========================================================

constrained = safety_allocation.copy()

constrained["constrained_share"] = constrained["safety_share"]

# Apply floors
for tier, floor in MIN_ALLOCATION_FLOOR.items():
    constrained.loc[
        constrained["validation_tier"] == tier,
        "constrained_share"
    ] = np.maximum(
        constrained.loc[
            constrained["validation_tier"] == tier,
            "constrained_share"
        ],
        floor
    )

# Apply caps
for tier, cap in MAX_ALLOCATION_CAP.items():
    constrained.loc[
        constrained["validation_tier"] == tier,
        "constrained_share"
    ] = np.minimum(
        constrained.loc[
            constrained["validation_tier"] == tier,
            "constrained_share"
        ],
        cap
    )

# Re-normalize to sum = 1
constrained["constrained_share"] = (
    constrained["constrained_share"] /
    constrained["constrained_share"].sum()
)

# ==========================================================
# MERGE RESULTS
# ==========================================================

final_allocation = pure_allocation.merge(
    safety_allocation,
    on="validation_tier"
).merge(
    constrained[["validation_tier", "constrained_share"]],
    on="validation_tier"
)

final_allocation["pure_%"] = final_allocation["pure_share"] * 100
final_allocation["safety_%"] = final_allocation["safety_share"] * 100
final_allocation["constrained_%"] = final_allocation["constrained_share"] * 100

final_allocation = final_allocation[[
    "validation_tier",
    "pure_%",
    "safety_%",
    "constrained_%"
]]

# ==========================================================
# SAVE OUTPUT
# ==========================================================

output_path = os.path.join(TABLE_DIR, "validation_allocation_comparison.csv")
final_allocation.to_csv(output_path, index=False)

print("\nValidation Allocation Comparison (%):")
print(final_allocation)

print("\nSaved allocation comparison to:", output_path)