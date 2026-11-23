# Task 1.2 — Inspect and clean, pass 1 (5 marks)

# Load the file with pd.read_csv. Print shape, info(), isnull().sum() and duplicated().sum(). Then, in this
# order: (a) drop exact duplicate rows; (b) clean booking_channel with .str.strip().str.title(); (c) convert
# appt_date with pd.to_datetime(..., errors="coerce") and booked_on with pd.to_datetime; (d) drop rows where
# appt_date is missing after conversion or status is missing. Print the row count after each step. This task
# starts again from the original appointments.csv: Task 1.1 is a separate exercise in reading with the csv
# module, so do not use its accepted/rejected lists here — the pandas cleaning in 1.2–1.3 is the one that
# feeds the rest of the project.

# Solution

# ==========================================
# CARELOOP CLINICS
# PART 1 - TASK 1.2
# Inspect and clean, pass 1
# ==========================================
import pandas as pd
from pathlib import Path

# Step 1: Read the original CSV file
file_path = Path(__file__).resolve().parent / "appointments.csv"

df = pd.read_csv(file_path)

print("========== STEP 1: ORIGINAL DATA ==========")

print("Original shape:", df.shape)
print("Original row count:", len(df))

# Step 2: Inspect the dataset
print("\n========== STEP 2: DATA INFORMATION ==========")

print("\nDataset information:")
df.info()

print("\nMissing values in each column:")
print(df.isnull().sum())

print("\nNumber of exact duplicate rows:")
print(df.duplicated().sum())

# Step 3: Drop exact duplicate rows
print("\n========== STEP 3: DROP DUPLICATES ==========")

df = df.drop_duplicates().copy()

print("Rows after dropping duplicates:", len(df))

# Step 4: Clean booking_channel
print("\n========== STEP 4: CLEAN BOOKING CHANNEL ==========")

df["booking_channel"] = (
    df["booking_channel"].str.strip().str.title()
)

print("Rows after cleaning booking_channel:", len(df))

print("\nBooking channel values:")
print(df["booking_channel"].value_counts(dropna=False))

# Step 5: Convert date columns into datetime format
print("\n========== STEP 5: CONVERT DATE COLUMNS ==========")

df["appt_date"] = pd.to_datetime(
    df["appt_date"], errors="coerce"
)

df["booked_on"] = pd.to_datetime(
    df["booked_on"], errors="coerce"
)

print("Rows after date conversion:", len(df))

print("\nDate column data types:")
print(df[["appt_date", "booked_on"]].dtypes)

# Step 6: Drop rows with missing appointment date or status
print("\n========== STEP 6: DROP MISSING VALUES ==========")

before_drop = len(df)

df = df.dropna(subset=["appt_date", "status"]).copy()

after_drop = len(df)

print("Rows before dropping missing values:", before_drop)
print("Rows removed:", before_drop - after_drop)
print("Final rows after cleaning:", after_drop)

# Step 7: Final dataset information
print("\n========== FINAL CLEANED DATA ==========")

print("Final shape:", df.shape)

print("\nRemaining missing values:")
print(df.isnull().sum())

print("\nTask 1.2 completed successfully!")