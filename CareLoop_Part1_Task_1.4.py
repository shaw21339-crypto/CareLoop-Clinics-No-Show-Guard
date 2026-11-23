# Task 1.4 — Features and a NumPy summary (4 marks)

# Create lead_days = days between booked_on and appt_date (use .dt.days) and no_show = 1 if status is
# "No-Show" else 0. Then take X = df[["age","distance_km","fee_inr","lead_days"]].to_numpy() and, without
# loops, compute: (a) the mean of each column (axis=0); (b) the number and share of rows with lead_days > 14
# using a boolean mask (mask.sum() counts the True values and mask.mean() gives the share); (c) z-scores
# of the distance_km column using (x - np.mean(x)) / np.std(x) and the count of rows with |z| > 2.

# Solution

# ==========================================
# CARELOOP CLINICS
# PART 1 - TASK 1.4
# Features and a NumPy summary
# ==========================================

import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# STEP 1: LOAD ORIGINAL CSV
# ==========================================

file_path = Path(__file__).resolve().parent / "appointments.csv"

df = pd.read_csv(file_path)

print("========== TASK 1.4 ==========")
print("Original rows:", len(df))

# ==========================================
# STEP 2: REPEAT TASK 1.2 CLEANING
# ==========================================

# Remove duplicate rows
df = df.drop_duplicates().copy()

# Clean booking channel
df["booking_channel"] = (
    df["booking_channel"].str.strip().str.title()
)

# Convert dates
df["appt_date"] = pd.to_datetime(
    df["appt_date"], errors="coerce"
)

df["booked_on"] = pd.to_datetime(
    df["booked_on"], errors="coerce"
)

# Remove missing appointment date and status
df = df.dropna(subset=["appt_date", "status"]).copy()

print("\nRows after Task 1.2 cleaning:", len(df))


# ==========================================
# STEP 3: REPEAT TASK 1.3 CLEANING
# ==========================================

# Validate age
df["age"] = pd.to_numeric(
    df["age"], errors="coerce"
)

invalid_age = (
    (df["age"] < 1) | (df["age"] > 100)
)

df.loc[invalid_age, "age"] = np.nan

# Fill missing age with median
age_median = df["age"].median()

df["age"] = (
    df["age"]
    .fillna(age_median)
    .round()
    .astype(int)
)

# Convert distance to numeric
df["distance_km"] = pd.to_numeric(
    df["distance_km"], errors="coerce"
)

# Fill missing distance with median
distance_median = df["distance_km"].median()

df["distance_km"] = df["distance_km"].fillna(
    distance_median
)

# Convert fee to numeric
df["fee_inr"] = pd.to_numeric(
    df["fee_inr"], errors="coerce"
)

# Calculate distance IQR
Q1_distance = df["distance_km"].quantile(0.25)
Q3_distance = df["distance_km"].quantile(0.75)

IQR_distance = Q3_distance - Q1_distance

lower_distance = Q1_distance - 1.5 * IQR_distance
upper_distance = Q3_distance + 1.5 * IQR_distance

# Cap distance outliers
df["distance_km"] = np.clip(
    df["distance_km"],
    lower_distance,
    upper_distance
)

# Calculate fee IQR
Q1_fee = df["fee_inr"].quantile(0.25)
Q3_fee = df["fee_inr"].quantile(0.75)

IQR_fee = Q3_fee - Q1_fee

lower_fee = Q1_fee - 1.5 * IQR_fee
upper_fee = Q3_fee + 1.5 * IQR_fee

# Cap fee outliers
df["fee_inr"] = np.clip(
    df["fee_inr"],
    lower_fee,
    upper_fee
)

# Round values
df["distance_km"] = df["distance_km"].round(1)

df["fee_inr"] = (
    df["fee_inr"].round().astype(int)
)

print("Rows after Task 1.3 cleaning:", len(df))


# ==========================================
# STEP 4: CREATE LEAD_DAYS FEATURE
# ==========================================

print("\n========== STEP 4: CREATE FEATURES ==========")

df["lead_days"] = (
    df["appt_date"] - df["booked_on"]
).dt.days

print("Lead days feature created successfully.")

# ==========================================
# STEP 5: CREATE NO_SHOW FEATURE
# ==========================================

df["no_show"] = (
    df["status"] == "No-Show"
).astype(int)

print("No-show feature created successfully.")

print("\nNo-show counts:")
print(df["no_show"].value_counts())


# ==========================================
# STEP 6: CREATE NUMPY ARRAY
# ==========================================

print("\n========== STEP 6: NUMPY ARRAY ==========")

X = df[
    ["age", "distance_km", "fee_inr", "lead_days"]
].to_numpy()

print("NumPy array:")
print(X)

print("\nArray shape:", X.shape)


# ==========================================
# STEP 7: CALCULATE COLUMN MEANS
# ==========================================

print("\n========== STEP 7: COLUMN MEANS ==========")

column_means = np.mean(X, axis=0)

print("Mean of each column:")
print(column_means)

print("Column order: age, distance_km, fee_inr, lead_days")


# ==========================================
# STEP 8: LEAD DAYS GREATER THAN 14
# ==========================================

print("\n========== STEP 8: LEAD DAYS ANALYSIS ==========")

mask = df["lead_days"] > 14

# Count rows where lead_days > 14
lead_count = mask.sum()

# Calculate share of rows
lead_share = mask.mean()

print("Rows with lead_days > 14:", lead_count)

print("Share of rows:", lead_share)

print("Percentage of rows:", lead_share * 100)


# ==========================================
# STEP 9: DISTANCE Z-SCORES
# ==========================================

print("\n========== STEP 9: DISTANCE Z-SCORES ==========")

x = X[:, 1]

z = (x - np.mean(x)) / np.std(x)

print("Distance Z-scores:")
print(z)

# Count rows where absolute Z-score > 2
z_count = np.sum(np.abs(z) > 2)

print("Rows with absolute Z-score > 2:", z_count)


# ==========================================
# STEP 10: FINAL RESULTS
# ==========================================

print("\n========== FINAL RESULTS ==========")

print("Final dataset shape:", df.shape)

print("Total no-show records:", df["no_show"].sum())

print("Total rows with lead_days > 14:", lead_count)

print("Total distance Z-score values above 2:", z_count)

print("\nTask 1.4 completed successfully!")