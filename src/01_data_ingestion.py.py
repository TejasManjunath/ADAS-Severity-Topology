import pandas as pd
import os

folder_path = r"D:\PROJECTS\adas-scenario-intelligence\Data\RAW_DATA"

files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

print("Files found:", files)

dfs = []

for file in files:
    full_path = os.path.join(folder_path, file)
    print("Loading:", full_path)
    
    df = pd.read_csv(full_path, sep=";", encoding="utf-8")
    dfs.append(df)

master_df = pd.concat(dfs, ignore_index=True)

print("Final dataset shape:", master_df.shape)

processed_path = r"D:\PROJECTS\adas-scenario-intelligence\Data\processed"

os.makedirs(processed_path, exist_ok=True)

master_df.to_pickle(os.path.join(processed_path, "master_accidents.pkl"))

master_df.to_csv(
    r"D:\PROJECTS\adas-scenario-intelligence\Data\processed\master_accidents.csv",
    index=False
)
print("Master dataset saved successfully.")
