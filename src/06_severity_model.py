"""
06_severity_model.py

Severity Amplification Model for ADAS Scenario Prioritization
Stable Production Version

Author: TEJAS MANJUNATH
"""

import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
from patsy import dmatrices
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "Data", "processed", "cleaned_accidents.pkl")

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
TABLE_DIR = os.path.join(OUTPUT_DIR, "tables")
MODEL_DIR = os.path.join(OUTPUT_DIR, "models")

for d in [FIG_DIR, TABLE_DIR, MODEL_DIR]:
    os.makedirs(d, exist_ok=True)

SAMPLE_FRAC = 0.3  # set to 1.0 for full model

# ==========================================================
# LOAD DATA
# ==========================================================

print("Loading dataset...")
df = pd.read_pickle(DATA_PATH)
print("Full dataset shape:", df.shape)

if SAMPLE_FRAC < 1.0:
    df = df.sample(frac=SAMPLE_FRAC, random_state=42)
    print("Using subsample shape:", df.shape)

baseline_rate = df["is_high_severity"].mean()
print("Baseline high severity rate:", round(baseline_rate, 4))

# ==========================================================
# FEATURE SELECTION
# ==========================================================

columns = [
    "is_high_severity",
    "accident_mechanism",
    "is_night",
    "state",
    "STRZUSTAND",
    "pedestrian_involved",
    "bicycle_involved",
    "motorcycle_involved",
    "heavy_vehicle_involved",
    "is_weekend",
    "USTUNDE"
]

df = df[columns].copy()

# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

# Hour bin
def hour_bin(h):
    if pd.isna(h):
        return "unknown"
    h = int(h)
    if h <= 5:
        return "late_night"
    elif h <= 11:
        return "morning"
    elif h <= 17:
        return "afternoon"
    else:
        return "evening"

df["hour_bin"] = df["USTUNDE"].apply(hour_bin)

# Clean mechanism
top_mechs = df["accident_mechanism"].value_counts().nlargest(15).index
df["mechanism_clean"] = df["accident_mechanism"].where(
    df["accident_mechanism"].isin(top_mechs),
    "Other"
)

# Clean states
top_states = df["state"].value_counts().nlargest(10).index
df["state_clean"] = df["state"].where(
    df["state"].isin(top_states),
    "Other"
)

# Convert flags to int
flag_cols = [
    "is_night",
    "pedestrian_involved",
    "bicycle_involved",
    "motorcycle_involved",
    "heavy_vehicle_involved",
    "is_weekend"
]

for col in flag_cols:
    df[col] = df[col].astype(int)

# Surface condition numeric
df["STRZUSTAND"] = pd.to_numeric(df["STRZUSTAND"], errors="coerce")

# Fill missing STRZUSTAND with median
df["STRZUSTAND"] = df["STRZUSTAND"].fillna(df["STRZUSTAND"].median())

# Drop rows where target missing
df = df.dropna(subset=["is_high_severity"])

print("Final dataset shape for modeling:", df.shape)

# ==========================================================
# MODEL FORMULA
# ==========================================================

formula = """
is_high_severity ~ 
C(mechanism_clean) +
C(state_clean) +
C(hour_bin) +
STRZUSTAND +
is_night +
is_weekend +
pedestrian_involved +
bicycle_involved +
motorcycle_involved +
heavy_vehicle_involved +

C(mechanism_clean):is_night +
C(mechanism_clean):motorcycle_involved +
C(mechanism_clean):heavy_vehicle_involved +
is_night:motorcycle_involved
"""

# ==========================================================
# BUILD MATRICES
# ==========================================================
print("Creating design matrices...")

# Ensure binary numeric target
df["is_high_severity"] = df["is_high_severity"].astype(int)

y, X = dmatrices(formula, df, return_type="dataframe")

# Keep only first column of y (binary target)
y = y.iloc[:, 0]

# Remove duplicate columns
X = X.loc[:, ~X.columns.duplicated()]

print("Design matrix shape:", X.shape)
print("Target shape:", y.shape)

print("Fitting logistic regression...")
model = sm.Logit(y, X)
result = model.fit(maxiter=100, disp=False)

print("Model fitting complete.")
# Save model summary
with open(os.path.join(MODEL_DIR, "severity_model_summary.txt"), "w") as f:
    f.write(result.summary2().as_text())

# ==========================================================
# ODDS RATIOS
# ==========================================================

params = result.params
conf = result.conf_int()

odds_ratios = pd.DataFrame({
    "odds_ratio": np.exp(params),
    "lower_ci": np.exp(conf[0]),
    "upper_ci": np.exp(conf[1]),
    "p_value": result.pvalues
}).sort_values("odds_ratio", ascending=False)

from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

odds_path = os.path.join(TABLE_DIR, f"odds_ratios_{timestamp}.csv")
significant_path = os.path.join(TABLE_DIR, f"significant_drivers_{timestamp}.csv")

odds_ratios.to_csv(odds_path)

significant = odds_ratios[odds_ratios["p_value"] < 0.01]
significant.to_csv(significant_path)

print(f"Saved odds ratios to: {odds_path}")
print(f"Saved significant drivers to: {significant_path}")

print("\nTop 10 Severity Amplifiers:")
print(odds_ratios.head(10))

# ==========================================================
# FOREST PLOT
# ==========================================================

top_plot = odds_ratios.head(20)

plt.figure(figsize=(8, 10))
plt.hlines(y=top_plot.index, xmin=top_plot["lower_ci"], xmax=top_plot["upper_ci"])
plt.scatter(top_plot["odds_ratio"], top_plot.index)
plt.axvline(1, linestyle="--")
plt.xlabel("Odds Ratio")
plt.title("Top Severity Amplifiers")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "05_odds_ratio_forest.png"), dpi=300)
plt.close()

print("\nAll outputs saved successfully.")

print("\nBuilding ADAS Scenario Priority Framework...")

scenario = df.groupby(
    ["mechanism_clean", "is_night", "motorcycle_involved",
     "heavy_vehicle_involved", "pedestrian_involved"]
).agg(
    total_accidents=("is_high_severity", "count"),
    severe_cases=("is_high_severity", "sum")
).reset_index()

scenario["severity_rate"] = scenario["severe_cases"] / scenario["total_accidents"]
scenario["excess_rate"] = scenario["severity_rate"] - baseline_rate
scenario["exposure_weight"] = np.log1p(scenario["total_accidents"])

scenario["vru_multiplier"] = 1.0
scenario.loc[scenario["motorcycle_involved"] == 1, "vru_multiplier"] *= 1.2
scenario.loc[scenario["pedestrian_involved"] == 1, "vru_multiplier"] *= 1.2

scenario["interaction_boost"] = 1.0
scenario.loc[
    (scenario["is_night"] == 1) &
    (scenario["motorcycle_involved"] == 1),
    "interaction_boost"
] = 1.15

scenario["AVPI"] = (
    scenario["excess_rate"].clip(lower=0) *
    scenario["exposure_weight"] *
    scenario["vru_multiplier"] *
    scenario["interaction_boost"]
)

scenario = scenario.sort_values("AVPI", ascending=False)

scenario.to_csv(os.path.join(TABLE_DIR, "adas_priority_index.csv"), index=False)

print("\nTop 15 ADAS Critical Scenarios:")
print(scenario.head(15))