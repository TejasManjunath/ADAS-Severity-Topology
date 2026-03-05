# Data Description

This project analyses **German national traffic accident data** to identify high-severity crash scenarios and evaluate their representation in ADAS validation protocols.

The dataset used in this analysis contains approximately **1.53 million police-reported traffic accidents recorded in Germany between 2019 and 2024**.

Due to **licensing restrictions and file size constraints**, the raw dataset is **not included in this repository**. However, the complete data processing pipeline used in the project is provided so the analysis can be reproduced.

---

# Data Source

The accident data originates from the official German national accident statistics maintained by:

**Statistische Ämter des Bundes und der Länder**  
(German Federal and State Statistical Offices)

Official portal:

https://unfallatlas.statistikportal.de

This dataset aggregates police-reported road traffic accidents across Germany and is commonly used for **traffic safety research and policy analysis**.

---

# Dataset Scope

| Attribute | Description |
|----------|-------------|
| Country | Germany |
| Coverage period | **2019 – 2024** |
| Number of accident records | ~1,530,000 |
| Raw dataset size | ~400 MB |
| Cleaned dataset size | ~180 MB |
| Data type | Police-reported traffic accidents |

Each row in the dataset represents a **single accident event**.

The dataset contains information about:

- crash severity
- crash mechanism / topology
- time and location of the accident
- road conditions
- types of road users involved

---

# Key Variables Used in the Project

The analysis uses a subset of variables relevant for crash severity modelling and scenario identification.

| Variable | Description |
|---------|-------------|
| `UKATEGORIE` | Injury severity category (fatal / severe / minor) |
| `USTUNDE` | Hour of accident (0–23) |
| `ULAND` | German federal state identifier |
| `STRZUSTAND` | Road surface condition |
| `accident_mechanism` | Crash mechanism classification (oncoming collision, leaving carriageway, etc.) |
| Participant indicators | Flags indicating pedestrian, motorcycle, bicycle, or heavy vehicle involvement |

Additional derived variables were created during preprocessing.

---

# Derived Features

The preprocessing pipeline constructs several derived variables used in the modelling and scenario analysis.

Examples include:

| Feature | Description |
|-------|-------------|
| `is_high_severity` | Binary flag for severe injury or fatal accident |
| `is_night` | Indicator for accidents occurring between 21:00 and 05:59 |
| `is_weekend` | Indicator for weekend crashes |
| `motorcycle_involved` | Motorcycle participation in accident |
| `pedestrian_involved` | Pedestrian involvement |
| `heavy_vehicle_involved` | Heavy goods vehicle or bus involvement |

Categorical variables such as crash mechanism and federal state are also **standardised and consolidated** to avoid sparse categories.

---

# Data Processing Pipeline

Raw accident data is processed through the following pipeline contained in the repository:


01_data_exploration.py
02_cleaning_pipeline.py
03_feature_engineering.py


Processing steps include:

• removal of administrative or irrelevant columns  
• standardisation of crash mechanism labels  
• consolidation of rare categories  
• creation of binary severity indicators  
• generation of environmental and participant features  

The cleaned dataset used for modelling is stored internally as:


cleaned_accidents.pkl


This dataset becomes the **input for all downstream analysis scripts**.

---

# Generated Data Tables

The repository includes **processed output tables** generated from the cleaned dataset.

These tables are stored in:


outputs/tables/


Examples include:

| File | Description |
|-----|-------------|
| `compound_amplification_analysis.csv` | Severity amplification across compound crash scenarios |
| `gap_analysis_table.csv` | Mapping of high-severity scenarios against Euro NCAP coverage |
| `srpi_ranking.csv` | Scenario Risk Priority Index ranking |
| `injury_topology_concentration.csv` | Distribution of severe injuries across crash mechanisms |
| `validation_resource_allocation.csv` | Prioritised validation resource allocation |

These tables allow readers to inspect the **analytical outputs without requiring access to the raw dataset**.

---

# Reproducibility

Although the raw accident dataset cannot be distributed in this repository, the project remains reproducible through the provided scripts.

To reproduce the analysis:

1. Obtain the accident dataset from the official German statistical portal.
2. Run the preprocessing pipeline:


02_cleaning_pipeline.py
03_feature_engineering.py


3. Execute the analysis scripts contained in the repository.

All figures and tables in:


outputs/figures/
outputs/tables/


were generated directly from this pipeline.

---

# Data Limitations

Several limitations should be considered when interpreting the dataset:

• The dataset contains **police-reported accidents only**, which may underrepresent minor crashes that are not reported.  
• Crash mechanism classification is determined by reporting officers and may contain inconsistencies across regions or years.  
• The dataset represents **Germany only**, and findings may not generalise directly to other countries with different traffic environments.

---

# Ethical and Privacy Considerations

The dataset used in this project contains **aggregated accident records only** and does not include personally identifiable information.

The analysis is conducted exclusively for **road safety research and ADAS validation investigation**.
