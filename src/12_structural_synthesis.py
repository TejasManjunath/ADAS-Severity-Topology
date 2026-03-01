"""
12_structural_synthesis.py

Integrates amplification, burden concentration,
and validation prioritization into a unified
severity topology summary.

Author: TEJAS MANJUNATH
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE_DIR = os.path.join(BASE_DIR, "outputs", "tables")

print("Loading structural tables...")

amplification = pd.read_csv(os.path.join(TABLE_DIR, "compound_amplification_analysis.csv"))
topology = pd.read_csv(os.path.join(TABLE_DIR, "injury_topology_concentration.csv"))
tiers = pd.read_csv(os.path.join(TABLE_DIR, "adas_validation_tiers.csv"))

# ==========================================================
# EXTRACT KEY STRUCTURAL FINDINGS
# ==========================================================

# Top 3 amplification structures
top_amp = amplification.head(3)[[
    "mechanism_clean",
    "severity_rate",
    "relative_amplification"
]]

# Top 5 severe burden mechanisms
top_burden = topology.head(5)[[
    "accident_mechanism",
    "severe_share_%"
]]

# Tier distribution
tier_summary = tiers.groupby("validation_tier").agg(
    total_scenarios=("validation_tier", "count")
).reset_index()

print("\n=== STRUCTURAL SEVERITY SYNTHESIS ===\n")

print("Top Amplification Structures:")
print(top_amp)

print("\nTop Severe Injury Burden Mechanisms:")
print(top_burden)

print("\nValidation Tier Distribution:")
print(tier_summary)

print("\nSYNTHESIS COMPLETE.")