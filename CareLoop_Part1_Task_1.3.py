# Task 1.3 — Clean, pass 2: validity, gaps and outliers (5 marks)

# Work in this order, so that the quartiles and fences in (c) are computed after the gaps are filled. (a)
# Treat any age below 1 or above 100 as invalid and set it to missing. (b) Fill missing age with the median
# (then .round().astype(int)) and missing distance_km with its median. (c) For distance_km and fee_inr,
# compute Q1, Q3 and IQR with .quantile, and cap values at Q3 + 1.5×IQR and Q1 − 1.5×IQR with np.clip. (d)
# Round distance_km to 1 decimal and fee_inr to whole rupees (.round().astype(int)). Print how many values
# you capped in each column.

# Soluiton

# ==========================================
# CARELOOP CLINICS
# PART 1 - TASK 1.3
# Clean, pass 2: validity, gaps and outliers
# ==========================================
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# STEP 1: LOAD ORIGINAL CSV
# ==========================================

file_path = Path(__file__).resolve().parent / "appointments.csv"

df = pd.read_csv(file_path)

print("========== TASK 1.3 ==========")
print("Original rows:", len(df))

# ==========================================
# REPEAT TASK 1.2 CLEANING
# ==========================================

# Remove exact duplicates
df = df.drop_duplicates().copy()

print("Rows after removing duplicates:", len(df))

# Clean booking_channel
df["booking_channel"] = (
    df["booking_channel"].str.strip().str.title()
)

# Convert date columns
df["appt_date"] = pd.to_datetime(
    df["appt_date"], errors="coerce"
)

df["booked_on"] = pd.to_datetime(
    df["booked_on"], errors="coerce"
)

# Remove missing appointment date and status
df = df.dropna(subset=["appt_date", "status"]).copy()

print("Rows after Task 1.2 cleaning:", len(df))


# ==========================================
# STEP 2: VALIDATE AGE
# ==========================================

print("\n========== STEP 2: AGE VALIDATION ==========")

df["age"] = pd.to_numeric(
    df["age"], errors="coerce"
)

# Find invalid ages
invalid_age = (
    (df["age"] < 1) | (df["age"] > 100)
)

print("Invalid age values:", invalid_age.sum())

# Replace invalid ages with missing values
df.loc[invalid_age, "age"] = np.nan


# ==========================================
# STEP 3: FILL MISSING VALUES
# ==========================================

print("\n========== STEP 3: FILL MISSING VALUES ==========")

# Fill missing age with median
age_median = df["age"].median()

df["age"] = (
    df["age"]
    .fillna(age_median)
    .round()
    .astype(int)
)

print("Age median:", age_median)
print("Missing age after filling:", df["age"].isna().sum())

# Fill missing distance with median
df["distance_km"] = pd.to_numeric(
    df["distance_km"], errors="coerce"
)

distance_median = df["distance_km"].median()

df["distance_km"] = df["distance_km"].fillna(
    distance_median
)

print("Distance median:", distance_median)
print(
    "Missing distance after filling:",
    df["distance_km"].isna().sum()
)


# ==========================================
# STEP 4: DISTANCE OUTLIERS USING IQR
# ==========================================

print("\n========== STEP 4: DISTANCE OUTLIERS ==========")

Q1_distance = df["distance_km"].quantile(0.25)
Q3_distance = df["distance_km"].quantile(0.75)

IQR_distance = Q3_distance - Q1_distance

lower_distance = Q1_distance - 1.5 * IQR_distance
upper_distance = Q3_distance + 1.5 * IQR_distance

print("Distance Q1:", Q1_distance)
print("Distance Q3:", Q3_distance)
print("Distance IQR:", IQR_distance)

print("Distance lower limit:", lower_distance)
print("Distance upper limit:", upper_distance)

# Count values outside the limits BEFORE capping
distance_capped = (
    (df["distance_km"] < lower_distance)
    | (df["distance_km"] > upper_distance)
)

print("Distance values capped:", distance_capped.sum())

# Cap distance values
df["distance_km"] = np.clip(
    df["distance_km"],
    lower_distance,
    upper_distance
)


# ==========================================
# STEP 5: FEE OUTLIERS USING IQR
# ==========================================

print("\n========== STEP 5: FEE OUTLIERS ==========")

df["fee_inr"] = pd.to_numeric(
    df["fee_inr"], errors="coerce"
)

Q1_fee = df["fee_inr"].quantile(0.25)
Q3_fee = df["fee_inr"].quantile(0.75)

IQR_fee = Q3_fee - Q1_fee

lower_fee = Q1_fee - 1.5 * IQR_fee
upper_fee = Q3_fee + 1.5 * IQR_fee

print("Fee Q1:", Q1_fee)
print("Fee Q3:", Q3_fee)
print("Fee IQR:", IQR_fee)

print("Fee lower limit:", lower_fee)
print("Fee upper limit:", upper_fee)

# Count values outside the limits BEFORE capping
fee_capped = (
    (df["fee_inr"] < lower_fee)
    | (df["fee_inr"] > upper_fee)
)

print("Fee values capped:", fee_capped.sum())

# Cap fee values
df["fee_inr"] = np.clip(
    df["fee_inr"],
    lower_fee,
    upper_fee
)


# ==========================================
# STEP 6: ROUND VALUES
# ==========================================

print("\n========== STEP 6: ROUND VALUES ==========")

# Distance to 1 decimal place
df["distance_km"] = df["distance_km"].round(1)

# Fee to whole rupees
df["fee_inr"] = (
    df["fee_inr"].round().astype(int)
)

print("Distance rounded to 1 decimal place.")
print("Fee rounded to whole rupees.")


# ==========================================
# STEP 7: FINAL RESULTS
# ==========================================

print("\n========== FINAL RESULTS ==========")

print("Final dataset shape:", df.shape)

print("Final age data type:", df["age"].dtype)
print("Final distance data type:", df["distance_km"].dtype)
print("Final fee data type:", df["fee_inr"].dtype)

print("\nTotal distance values capped:", distance_capped.sum())
print("Total fee values capped:", fee_capped.sum())

print("\nTask 1.3 completed successfully!")