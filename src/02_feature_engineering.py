import pandas as pd
import os

# =====================================================
# 1. PATH SETUP (Portable - No Hardcoded D:\ Paths)
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processed_path = os.path.join(BASE_DIR, "Data", "processed")

master_path = os.path.join(processed_path, "master_accidents.pkl")

print("Loading master dataset...")
master_df = pd.read_pickle(master_path)
print("Loaded master dataset:", master_df.shape)


# =====================================================
# 2. SELECT RELEVANT COLUMNS (MATCHES YOUR REAL SCHEMA)
# =====================================================

columns_to_keep = [
    "ULAND",          # location of the accident occured(states described in the dataset)
    "UJAHR",          # Year
    "UMONAT",         # Month
    "USTUNDE",        # Hour
    "UWOCHENTAG",     # Day of week
    "UKATEGORIE",     # Severity
    "UART",           # Road type
    "UTYP1",          # Accident type
    "ULICHTVERH",     # Light condition
    "STRZUSTAND",     # Road surface condition (corrected)
    "IstRad",
    "IstPKW",
    "IstFuss",
    "IstKrad",
    "IstGkfz"
]

existing_cols = [col for col in columns_to_keep if col in master_df.columns]
df = master_df[existing_cols].copy()

print("Columns used:", existing_cols)
print("Reduced dataset shape:", df.shape)


# =====================================================
# 3. CLEAN SEVERITY COLUMN
# =====================================================

df = df.dropna(subset=["UKATEGORIE"])

print("\nSeverity distribution:")
print(df["UKATEGORIE"].value_counts())

print("\nSeverity distribution (percentage):")
print(df["UKATEGORIE"].value_counts(normalize=True))


# =====================================================
# 4. CREATE SAFETY FLAGS
# =====================================================

df["is_fatal"] = df["UKATEGORIE"] == 1
df["is_severe"] = df["UKATEGORIE"] == 2
df["is_minor"] = df["UKATEGORIE"] == 3

df["is_high_severity"] = df["is_fatal"] | df["is_severe"]

overall_high_severity_rate = df["is_high_severity"].mean()

print("\nOverall High Severity Rate:", round(overall_high_severity_rate, 4))


# =====================================================
# 5. LIGHTING FLAGS
# =====================================================

print("\nLighting distribution:")
print(df["ULICHTVERH"].value_counts())

df["is_night"] = df["ULICHTVERH"] == 2
df["is_twilight"] = df["ULICHTVERH"] == 1
df["is_daylight"] = df["ULICHTVERH"] == 0


# =====================================================
# 6. PARTICIPANT FLAGS (CRITICAL FOR ADAS THINKING)
# =====================================================

df["pedestrian_involved"] = df["IstFuss"] == 1
df["bicycle_involved"] = df["IstRad"] == 1
df["motorcycle_involved"] = df["IstKrad"] == 1
df["heavy_vehicle_involved"] = df["IstGkfz"] == 1


# =====================================================
# 7. TIME-BASED FEATURES
# =====================================================

df["is_late_night_hour"] = df["USTUNDE"].isin([22, 23, 0, 1, 2, 3, 4])

df["is_weekend"] = df["UWOCHENTAG"].isin([6, 7])  # Assuming 6/7 = weekend


# =====================================================
# 8. SAVE CLEANED DATASET
# =====================================================
# ---------------------------------------------------
# Add state mapping (ULAND → state name)
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

df["ULAND"] = df["ULAND"].astype(int)
df["state"] = df["ULAND"].map(state_mapping)

# ---------------------------------------------------
# Accident Mechanism Mapping (UART → readable label)
# ---------------------------------------------------

mechanism_mapping = {
    1: "Collision - vehicle ahead",
    2: "Collision - lateral same direction",
    3: "Collision - turning/crossing vehicle",
    4: "Collision - oncoming vehicle",
    5: "Collision - stationary vehicle",
    6: "Collision - vehicle vs pedestrian",
    7: "Collision - obstacle in carriageway",
    8: "Leaving carriageway (right)",
    9: "Leaving carriageway (left)",
    0: "Other accident"
}

df["UART"] = df["UART"].astype(int)
df["accident_mechanism"] = df["UART"].map(mechanism_mapping)

cleaned_path = os.path.join(processed_path, "cleaned_accidents.pkl")
df.to_pickle(cleaned_path)

print("\nCleaned dataset saved at:", cleaned_path)
print("Final cleaned dataset shape:", df.shape)