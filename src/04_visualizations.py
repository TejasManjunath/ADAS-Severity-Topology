import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------
# 1. Resolve Project Paths (Professional Structure)
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "Data", "processed", "cleaned_accidents.pkl")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Create outputs folder if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading dataset from:", DATA_PATH)

df = pd.read_pickle(DATA_PATH)

print("Dataset shape:", df.shape)
print("Available columns:", df.columns.tolist())

# ---------------------------------------------------
# 2. Baseline Severity
# ---------------------------------------------------

baseline = df["is_high_severity"].mean()
print("Baseline High Severity Rate:", round(baseline, 4))

# ---------------------------------------------------
# 3. Visualization 1 – Severity by Mechanism
# ---------------------------------------------------

mechanism = (
    df.groupby("accident_mechanism")
      .agg(total=("is_high_severity", "count"),
           severe=("is_high_severity", "sum"))
)

mechanism["severity_rate"] = mechanism["severe"] / mechanism["total"]
mechanism = mechanism.sort_values("severity_rate", ascending=False)

plt.figure()
mechanism["severity_rate"].plot(kind="bar")
plt.axhline(baseline)
plt.title("Severity Rate by Accident Mechanism")
plt.ylabel("High Severity Rate")
plt.xticks(rotation=90)
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "fig_mechanism_severity.png"))
plt.close()

print("Saved: fig_mechanism_severity.png")

# ---------------------------------------------------
# 4. Visualization 2 – State × Mechanism Heatmap
# ---------------------------------------------------

selected_states = ["Thuringia", "Bavaria", "Berlin"]

df_selected = df[df["state"].isin(selected_states)]

heatmap_data = (
    df_selected.groupby(["state", "accident_mechanism"])
    .agg(total=("is_high_severity", "count"),
         severe=("is_high_severity", "sum"))
)

heatmap_data["severity_rate"] = (
    heatmap_data["severe"] / heatmap_data["total"]
)

heatmap_pivot = heatmap_data.reset_index().pivot(
    index="state",
    columns="accident_mechanism",
    values="severity_rate"
)

plt.figure()
sns.heatmap(heatmap_pivot)
plt.title("Severity Heatmap: State × Mechanism")
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "fig_state_mechanism_heatmap.png"))
plt.close()

print("Saved: fig_state_mechanism_heatmap.png")

# ---------------------------------------------------
# 5. Visualization 3 – Hour-of-Day Severity Curve
# ---------------------------------------------------

hour_data = (
    df_selected.groupby(["state", "USTUNDE"])
    .agg(total=("is_high_severity", "count"),
         severe=("is_high_severity", "sum"))
)

hour_data["severity_rate"] = hour_data["severe"] / hour_data["total"]
hour_data = hour_data.reset_index()

plt.figure()

for state in selected_states:
    subset = hour_data[hour_data["state"] == state]
    plt.plot(subset["USTUNDE"], subset["severity_rate"], label=state)

plt.title("Severity Rate by Hour of Day")
plt.xlabel("Hour")
plt.ylabel("High Severity Rate")
plt.legend()
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "fig_hourly_severity.png"))
plt.close()

print("Saved: fig_hourly_severity.png")

# ---------------------------------------------------
# 6. Visualization 4 – Final Amplifier Framework
# ---------------------------------------------------

summary_data = [
    ("Run-Off-Road (Leaving Carriageway)", 0.35),
    ("Oncoming Collision", 0.30),
    ("Vehicle vs Pedestrian", 0.28),
    ("Late Evening Rural Hours", 0.30),
]

summary_df = pd.DataFrame(
    summary_data,
    columns=["Amplifier", "Representative_Severity_Rate"]
)

summary_df["Baseline_Rate"] = baseline
summary_df["Relative_Amplification"] = (
    summary_df["Representative_Severity_Rate"] / baseline
)

plt.figure()
plt.bar(summary_df["Amplifier"], summary_df["Relative_Amplification"])
plt.title("Severity Amplification Framework")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "fig_amplifier_framework.png"))
plt.close()

print("Saved: fig_amplifier_framework.png")

print("\nAll visualizations successfully generated.")