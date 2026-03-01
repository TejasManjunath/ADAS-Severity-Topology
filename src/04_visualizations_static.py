import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------
# THEME CONFIGURATION
# ---------------------------------------------------

PRIMARY_BLUE = "#0B3C5D"
HIGHLIGHT_RED = "#B22222"
BASELINE_GRAY = "#444444"

plt.style.use("default")
sns.set_style("whitegrid")

# ---------------------------------------------------
# PATH SETUP
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "Data", "processed", "cleaned_accidents.pkl")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "figures")

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_pickle(DATA_PATH)

baseline = df["is_high_severity"].mean()

# ---------------------------------------------------
# 1. SEVERITY AMPLIFICATION BY MECHANISM
# ---------------------------------------------------

mechanism = (
    df.groupby("accident_mechanism")
      .agg(total=("is_high_severity","count"),
           severe=("is_high_severity","sum"))
)

mechanism["severity_rate"] = mechanism["severe"] / mechanism["total"]
mechanism = mechanism.sort_values("severity_rate", ascending=False)

# Keep top 6 only for clarity
mechanism = mechanism.head(6)

colors = [HIGHLIGHT_RED if i == 0 else PRIMARY_BLUE for i in range(len(mechanism))]

plt.figure(figsize=(10,6))
bars = plt.barh(mechanism.index, mechanism["severity_rate"], color=colors)
plt.axvline(baseline, color=BASELINE_GRAY, linestyle="--", linewidth=2)

for i, rate in enumerate(mechanism["severity_rate"]):
    plt.text(rate + 0.005, i, f"{rate:.2%}", va="center")

plt.title("Top Severity Amplifying Accident Mechanisms")
plt.xlabel("High Severity Rate")
plt.tight_layout()
plt.gca().invert_yaxis()

plt.savefig(os.path.join(OUTPUT_DIR, "01_mechanism_amplification.png"), dpi=300)
plt.close()

# ---------------------------------------------------
# 2. MECHANISMS ABOVE BASELINE
# ---------------------------------------------------

above_baseline = mechanism[mechanism["severity_rate"] > baseline]

plt.figure(figsize=(8,5))
plt.bar(above_baseline.index, above_baseline["severity_rate"], color=PRIMARY_BLUE)
plt.axhline(baseline, color=BASELINE_GRAY, linestyle="--", linewidth=2)

plt.xticks(rotation=45, ha="right")

for i, rate in enumerate(above_baseline["severity_rate"]):
    increase = (rate / baseline - 1) * 100
    plt.text(i, rate + 0.005, f"+{increase:.0f}%", ha="center")

plt.title("Mechanisms Above Baseline Severity")
plt.ylabel("High Severity Rate")
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "02_above_baseline.png"), dpi=300)
plt.close()

# ---------------------------------------------------
# 3. HOURLY SEVERITY CURVE (RURAL VS URBAN)
# ---------------------------------------------------

selected_states = ["Thuringia", "Bavaria", "Berlin"]
df_selected = df[df["state"].isin(selected_states)]

hour_data = (
    df_selected.groupby(["state","USTUNDE"])
    .agg(total=("is_high_severity","count"),
         severe=("is_high_severity","sum"))
)

hour_data["severity_rate"] = hour_data["severe"] / hour_data["total"]
hour_data = hour_data.reset_index()

plt.figure(figsize=(10,6))

for state in selected_states:
    subset = hour_data[hour_data["state"] == state]
    plt.plot(subset["USTUNDE"], subset["severity_rate"], label=state)

# Highlight late-night zone
plt.axvspan(20, 24, color=HIGHLIGHT_RED, alpha=0.1)
plt.axvspan(0, 5, color=HIGHLIGHT_RED, alpha=0.1)

plt.axhline(baseline, color=BASELINE_GRAY, linestyle="--")

plt.title("Hourly Severity Rate by State")
plt.xlabel("Hour of Day")
plt.ylabel("High Severity Rate")
plt.legend()
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "03_hourly_risk_curve.png"), dpi=300)
plt.close()

# ---------------------------------------------------
# 4. STATE × MECHANISM HEATMAP (TOP MECHANISMS)
# ---------------------------------------------------

top_mechs = mechanism.index.tolist()

heat_data = (
    df_selected[df_selected["accident_mechanism"].isin(top_mechs)]
    .groupby(["state","accident_mechanism"])
    .agg(total=("is_high_severity","count"),
         severe=("is_high_severity","sum"))
)

heat_data["severity_rate"] = heat_data["severe"] / heat_data["total"]

heat_pivot = heat_data.reset_index().pivot(
    index="state",
    columns="accident_mechanism",
    values="severity_rate"
)

plt.figure(figsize=(10,6))
sns.heatmap(
    heat_pivot,
    annot=True,
    fmt=".2f",
    cmap="Blues",
    center=baseline
)

plt.title("Severity Amplification by State and Mechanism")
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "04_state_mechanism_heatmap.png"), dpi=300)
plt.close()

print("Professional static figures generated successfully.")