import pandas as pd
import os

# Load cleaned dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processed_path = os.path.join(BASE_DIR, "Data", "processed")

df = pd.read_pickle(os.path.join(processed_path, "cleaned_accidents.pkl"))

print("Dataset loaded:", df.shape)

# ---------------------------------------------------
# 1. Lighting-Based Risk Analysis
# ---------------------------------------------------

lighting_risk = df.groupby("ULICHTVERH").agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

lighting_risk["high_severity_rate"] = (
    lighting_risk["high_severity_cases"] /
    lighting_risk["total_accidents"]
)

print("\nLighting Risk Table:")
print(lighting_risk)

# ---------------------------------------------------
# 2. Pedestrian Risk Analysis
# ---------------------------------------------------

pedestrian_risk = df.groupby("pedestrian_involved").agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

pedestrian_risk["high_severity_rate"] = (
    pedestrian_risk["high_severity_cases"] /
    pedestrian_risk["total_accidents"]
)

print("\nPedestrian Risk Table:")
print(pedestrian_risk)

# ---------------------------------------------------
# 3. Night + Pedestrian Combined Risk
# ---------------------------------------------------

night_pedestrian = df.groupby(
    ["is_night", "pedestrian_involved"]
).agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

night_pedestrian["high_severity_rate"] = (
    night_pedestrian["high_severity_cases"] /
    night_pedestrian["total_accidents"]
)

print("\nNight + Pedestrian Risk Table:")
print(night_pedestrian)

# ---------------------------------------------------
# 4. Multi-Factor Scenario Risk Ranking
# ---------------------------------------------------

scenario_cols = [
    "ULICHTVERH",
    "pedestrian_involved",
    "bicycle_involved"
]

scenario_risk = df.groupby(scenario_cols).agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

scenario_risk["high_severity_rate"] = (
    scenario_risk["high_severity_cases"] /
    scenario_risk["total_accidents"]
)

# Filter small samples to avoid statistical noise
scenario_risk = scenario_risk[scenario_risk["total_accidents"] > 1000]

scenario_risk = scenario_risk.sort_values(
    by="high_severity_rate",
    ascending=False
)

print("\nTop 10 High-Risk Scenarios:")
print(scenario_risk.head(10))

# ---------------------------------------------------
# 5. Relative Risk Index (Validation-Oriented)
# ---------------------------------------------------

baseline_rate = df["is_high_severity"].mean()

scenario_risk["relative_risk_index"] = (
    scenario_risk["high_severity_rate"] / baseline_rate
)

# Filter statistically weak samples
scenario_risk = scenario_risk[scenario_risk["total_accidents"] > 5000]

scenario_risk = scenario_risk.sort_values(
    by="relative_risk_index",
    ascending=False
)

print("\nRelative Risk Ranking (Validation Focused):")
print(scenario_risk.head(10))

# ---------------------------------------------------
# 6. Decode Accident Mechanism (UART)
# ---------------------------------------------------

uart_mapping = {
    0: "Other accident",
    1: "Collision - stationary vehicle",
    2: "Collision - vehicle ahead",
    3: "Collision - lateral same direction",
    4: "Collision - oncoming vehicle",
    5: "Collision - turning/crossing vehicle",
    6: "Collision - vehicle vs pedestrian",
    7: "Collision - obstacle in carriageway",
    8: "Leaving carriageway (right)",
    9: "Leaving carriageway (left)"
}

df["accident_mechanism"] = df["UART"].map(uart_mapping)


# ---------------------------------------------------
# 7. Mechanism + Lighting + VRU Risk Ranking
# ---------------------------------------------------

scenario_cols = [
    "accident_mechanism",
    "ULICHTVERH",
    "pedestrian_involved"
]

mechanism_risk = df.groupby(scenario_cols).agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

mechanism_risk["high_severity_rate"] = (
    mechanism_risk["high_severity_cases"] /
    mechanism_risk["total_accidents"]
)

baseline_rate = df["is_high_severity"].mean()

mechanism_risk["relative_risk_index"] = (
    mechanism_risk["high_severity_rate"] / baseline_rate
)

# Remove statistically weak scenarios
mechanism_risk = mechanism_risk[mechanism_risk["total_accidents"] > 5000]

mechanism_risk = mechanism_risk.sort_values(
    by="relative_risk_index",
    ascending=False
)

print("\nMechanism-Based Validation Risk Ranking:")
print(mechanism_risk.head(10))

# ---------------------------------------------------
# 8. State-Level Severity Ranking
# ---------------------------------------------------

state_mapping = {
    1: "Schleswig-Holstein",
    2: "Hamburg",
    3: "Lower Saxony",
    4: "Bremen",
    5: "North Rhine-Westphalia",
    6: "Hesse",
    7: "Rhineland-Palatinate",
    8: "Baden-Württemberg",
    9: "Bavaria",
    10: "Saarland",
    11: "Berlin",
    12: "Brandenburg",
    13: "Mecklenburg-Vorpommern",
    14: "Saxony",
    15: "Saxony-Anhalt",
    16: "Thuringia"
}

df["state"] = df["ULAND"].astype(int).map(state_mapping)

state_risk = df.groupby("state").agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

state_risk["high_severity_rate"] = (
    state_risk["high_severity_cases"] /
    state_risk["total_accidents"]
)

baseline_rate = df["is_high_severity"].mean()

state_risk["relative_risk_index"] = (
    state_risk["high_severity_rate"] / baseline_rate
)

state_risk = state_risk.sort_values(
    by="relative_risk_index",
    ascending=False
)

print("\nState-Level Severity Ranking:")
print(state_risk)

# ---------------------------------------------------
# 9. Focused Regional Comparison (3 States)
# ---------------------------------------------------

selected_states = ["Thuringia", "Bavaria", "Berlin"]

df_selected = df[df["state"].isin(selected_states)]

print("\nSelected State Counts:")
print(df_selected["state"].value_counts())


# ---------------------------------------------------
# Surface Condition × State Severity
# ---------------------------------------------------

state_surface = df_selected.groupby(
    ["state", "STRZUSTAND"]
).agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

state_surface["high_severity_rate"] = (
    state_surface["high_severity_cases"] /
    state_surface["total_accidents"]
)

print("\nState × Surface Severity Table:")
print(state_surface)

state_mechanism = df_selected.groupby(
    ["state", "accident_mechanism"]
).agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

state_mechanism["high_severity_rate"] = (
    state_mechanism["high_severity_cases"] /
    state_mechanism["total_accidents"]
)

print(state_mechanism.sort_values("high_severity_rate", ascending=False))

# ---------------------------------------------------
# Mechanism × State Severity Amplification
# ---------------------------------------------------

state_mechanism = df_selected.groupby(
    ["state", "accident_mechanism"]
).agg(
    total_accidents=("UKATEGORIE", "count"),
    high_severity_cases=("is_high_severity", "sum")
)

state_mechanism["high_severity_rate"] = (
    state_mechanism["high_severity_cases"] /
    state_mechanism["total_accidents"]
)

print("\nState × Mechanism Severity:")
print(state_mechanism.sort_values("high_severity_rate", ascending=False))

hour_severity = df_selected.groupby(
    ["state", "USTUNDE"]
).agg(
    high_severity_rate=("is_high_severity", "mean")
)

print(hour_severity)

# ---------------------------------------------------
# Final Severity Amplifier Summary
# ---------------------------------------------------

baseline_rate = df["is_high_severity"].mean()

summary_data = [
    ("Run-Off-Road (Leaving Carriageway)", 0.35),
    ("Oncoming Collision", 0.30),
    ("Vehicle vs Pedestrian", 0.28),
    ("Late Evening Rural Hours", 0.30),
]

import pandas as pd

summary_df = pd.DataFrame(summary_data, columns=["Amplifier", "Representative_Severity_Rate"])

summary_df["Baseline_Rate"] = baseline_rate
summary_df["Relative_Amplification"] = (
    summary_df["Representative_Severity_Rate"] / baseline_rate
)

print("\nFinal Severity Amplifier Framework:")
print(summary_df)