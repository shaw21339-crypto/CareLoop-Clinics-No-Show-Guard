# Task 2.3 — Does booking far ahead matter? (4 marks)
# Using CASE WHEN, put lead_days into four bands (the labels must come out of the CASE WHEN, not be typed
# into the data) — 1-7, 8-14, 15-30, 31+ (upper limits inclusive: 7, 14 and 30 belong to the lower band) —
# and show appointments, no-shows and no_show_pct per band in band order (hint: ORDER BY MIN(lead_days) sorts
# the bands by how short their lead times are, whereas sorting by the band text would put 15-30 before 8-14).

# Solution
# ==========================================
#  CARELOOP CLINICS
#  PART 2 - TASK 2.3
#   Does booking far ahead matter?
#  ==========================================

import pandas as pd

# Step 1: Load the cleaned appointment dataset
df = pd.read_csv("appointments_clean.csv")

# Step 2: Convert columns into numeric format
df["lead_days"] = pd.to_numeric(
    df["lead_days"], errors="coerce"
)

df["no_show"] = pd.to_numeric(
    df["no_show"], errors="coerce"
)

# Step 3: Create booking bands
df["lead_band"] = pd.cut(
    df["lead_days"],
    bins=[0, 7, 14, 30, float("inf")],
    labels=["1-7", "8-14", "15-30", "31+"],
    right=True
)

# Step 4: Group the data
result = df.groupby(
    "lead_band",
    observed=False
).agg(
    appointments=("no_show", "size"),
    no_shows=("no_show", "sum")
).reset_index()

# Step 5: Calculate no-show percentage
result["no_show_pct"] = (
    result["no_shows"] /
    result["appointments"] * 100
).round(1)

# Step 6: Display results
print("BOOKING LEAD-TIME ANALYSIS")
print(result.to_string(index=False))

# Step 7: Display totals
print("\nTOTAL APPOINTMENTS:", result["appointments"].sum())
print("TOTAL NO-SHOWS:", result["no_shows"].sum())