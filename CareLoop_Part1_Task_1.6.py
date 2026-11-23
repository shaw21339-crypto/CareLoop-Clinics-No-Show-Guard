# Task 1.6 — Export the clean table and write the SQL load script (4 marks)

# Sort the cleaned data by appointment_id, format both date columns as YYYY-MM-DD text (.dt.strftime
# ("%Y-%m-%d")), and save appointments_clean.csv with exactly these 16 columns, in this order: appointment_id,
# patient_id, clinic_id, booked_on, appt_date, age, gender, distance_km, fee_inr, booking_channel, visit_type,
# reminder_sent, prior_no_shows, status, lead_days, no_show. Then, with a for loop and f-strings, write
# load_data.sql containing one statement per row, in this pattern (text in single quotes, numbers unquoted):
# INSERT INTO appointments VALUES ('A0001','P196','C05','2025-01-22',...,0); — and likewise one INSERT INTO
# clinics VALUES (...) per clinic from clinics_enriched.csv. Write all the clinics statements first, because
# the appointments table points to them with a foreign key. Before exporting, check and print that
# appointment_id is unique and that none of the 16 columns has a missing value. (Building SQL text with
# f-strings is fine for this fixed, controlled dataset — none of its values contains an apostrophe.
# It is not a safe method for real applications, where parameterised queries are used instead.)

# Solution
# ==========================================
# CARELOOP CLINICS
# PART 1 - TASK 1.6
# Export the clean table and write the SQL load script
# ==========================================
import pandas as pd
import numpy as np
from pathlib import Path
import numbers

# ==========================================
# STEP 1: LOAD ORIGINAL APPOINTMENT DATA
# ==========================================

folder = Path(__file__).resolve().parent

input_file = folder / "appointments.csv"
clinic_file = folder / "clinics_enriched.csv"

df = pd.read_csv(input_file)

print("========== TASK 1.6 ==========")
print("Original rows:", len(df))


# ==========================================
# STEP 2: CLEAN APPOINTMENT DATA
# ==========================================

# Remove exact duplicate rows
df = df.drop_duplicates().copy()

print("After removing duplicates:", len(df))

# Clean booking channel
df["booking_channel"] = (
    df["booking_channel"]
    .astype("string")
    .str.strip()
    .str.title()
)

# Convert date columns
df["appt_date"] = pd.to_datetime(
    df["appt_date"], errors="coerce"
)

df["booked_on"] = pd.to_datetime(
    df["booked_on"], errors="coerce"
)

# Drop missing appointment date and status
df = df.dropna(
    subset=["appt_date", "status"]
).copy()

print("After date/status cleaning:", len(df))


# ==========================================
# STEP 3: VALIDATE AGE
# ==========================================

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


# ==========================================
# STEP 4: FILL MISSING DISTANCE
# ==========================================

df["distance_km"] = pd.to_numeric(
    df["distance_km"], errors="coerce"
)

distance_median = df["distance_km"].median()

df["distance_km"] = df["distance_km"].fillna(
    distance_median
)


# ==========================================
# STEP 5: CAP DISTANCE OUTLIERS
# ==========================================

Q1_distance = df["distance_km"].quantile(0.25)
Q3_distance = df["distance_km"].quantile(0.75)

IQR_distance = Q3_distance - Q1_distance

lower_distance = (
    Q1_distance - 1.5 * IQR_distance
)

upper_distance = (
    Q3_distance + 1.5 * IQR_distance
)

df["distance_km"] = np.clip(
    df["distance_km"],
    lower_distance,
    upper_distance
)

df["distance_km"] = df["distance_km"].round(1)


# ==========================================
# STEP 6: CAP FEE OUTLIERS
# ==========================================

df["fee_inr"] = pd.to_numeric(
    df["fee_inr"], errors="coerce"
)

Q1_fee = df["fee_inr"].quantile(0.25)
Q3_fee = df["fee_inr"].quantile(0.75)

IQR_fee = Q3_fee - Q1_fee

lower_fee = Q1_fee - 1.5 * IQR_fee
upper_fee = Q3_fee + 1.5 * IQR_fee

df["fee_inr"] = np.clip(
    df["fee_inr"],
    lower_fee,
    upper_fee
)

df["fee_inr"] = (
    df["fee_inr"].round().astype("Int64")
)


# ==========================================
# STEP 7: CREATE LEAD_DAYS AND NO_SHOW
# ==========================================

df["lead_days"] = (
    df["appt_date"] - df["booked_on"]
).dt.days

df["no_show"] = (
    df["status"] == "No-Show"
).astype(int)


# ==========================================
# STEP 8: SELECT EXACT 16 COLUMNS
# ==========================================

columns = [
    "appointment_id",
    "patient_id",
    "clinic_id",
    "booked_on",
    "appt_date",
    "age",
    "gender",
    "distance_km",
    "fee_inr",
    "booking_channel",
    "visit_type",
    "reminder_sent",
    "prior_no_shows",
    "status",
    "lead_days",
    "no_show"
]

df = df[columns].copy()


# ==========================================
# STEP 9: FORMAT DATE COLUMNS
# ==========================================

df["booked_on"] = (
    df["booked_on"].dt.strftime("%Y-%m-%d")
)

df["appt_date"] = (
    df["appt_date"].dt.strftime("%Y-%m-%d")
)


# ==========================================
# STEP 10: SORT BY APPOINTMENT ID
# ==========================================

df = df.sort_values(
    by="appointment_id"
).reset_index(drop=True)


# ==========================================
# STEP 11: VALIDATE FINAL DATA
# ==========================================

print("\n========== DATA VALIDATION ==========")

print("Final shape:", df.shape)

# Check appointment ID uniqueness
unique_ids = df["appointment_id"].is_unique

print("Appointment IDs unique:", unique_ids)

# Check missing values
missing_values = df.isna().sum()

print("\nMissing values in each column:")
print(missing_values)

if not unique_ids:
    raise ValueError("Duplicate appointment IDs found!")

if df.isna().any().any():
    raise ValueError(
        "Missing values found in appointment data. "
        "Check the columns printed above."
    )

if len(df.columns) != 16:
    raise ValueError("Expected exactly 16 columns!")


# ==========================================
# STEP 12: EXPORT CLEAN APPOINTMENT CSV
# ==========================================

clean_file = folder / "appointments_clean.csv"

df.to_csv(
    clean_file,
    index=False
)

print("\nClean CSV saved:", clean_file.name)


# ==========================================
# STEP 13: LOAD ENRICHED CLINIC DATA
# ==========================================

if not clinic_file.exists():
    raise FileNotFoundError(
        "clinics_enriched.csv not found. "
        "Run Task 1.5 first."
    )

clinics = pd.read_csv(clinic_file)

print("\nTotal clinics:", len(clinics))

if len(clinics) != 8:
    raise ValueError(
        "Expected exactly 8 clinic records!"
    )


# ==========================================
# STEP 14: CREATE SQL VALUE CONVERTER
# ==========================================

def sql_value(value):

    # Missing values become SQL NULL
    if pd.isna(value):
        return "NULL"

    # Convert NumPy values to Python values
    if isinstance(value, np.generic):
        value = value.item()

    # Numbers remain unquoted
    if isinstance(value, numbers.Number):
        return str(value)

    # Text values use single quotes
    text_value = str(value)

    return "'" + text_value.replace("'", "''") + "'"


# ==========================================
# STEP 15: GENERATE SQL SCRIPT
# ==========================================

sql_lines = []

# First insert all clinic records
print("\n========== GENERATING CLINIC SQL ==========")

for _, row in clinics.iterrows():

    values = [
        sql_value(value)
        for value in row.tolist()
    ]

    statement = (
        "INSERT INTO clinics VALUES ("
        + ", ".join(values)
        + ");"
    )

    sql_lines.append(statement)

print("Clinic SQL statements:", len(clinics))


# Then insert all appointment records
print("\n========== GENERATING APPOINTMENT SQL ==========")

for _, row in df.iterrows():

    values = [
        sql_value(value)
        for value in row.tolist()
    ]

    statement = (
        "INSERT INTO appointments VALUES ("
        + ", ".join(values)
        + ");"
    )

    sql_lines.append(statement)

print("Appointment SQL statements:", len(df))


# ==========================================
# STEP 16: SAVE SQL FILE
# ==========================================

sql_file = folder / "load_data.sql"

with open(
    sql_file,
    "w",
    encoding="utf-8"
) as file:

    file.write("\n".join(sql_lines))
    file.write("\n")


# ==========================================
# STEP 17: FINAL RESULTS
# ==========================================

print("\n========== TASK 1.6 FINAL RESULTS ==========")

print("Clean appointment rows:", len(df))
print("Appointment columns:", len(df.columns))

print("Unique appointment IDs:", unique_ids)

print("Missing appointment values:", df.isna().sum().sum())

print("Clinic SQL statements:", len(clinics))
print("Appointment SQL statements:", len(df))

print("Clean CSV:", clean_file.name)
print("SQL file:", sql_file.name)

print("\nTASK 1.6 COMPLETED SUCCESSFULLY!")