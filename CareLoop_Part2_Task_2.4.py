# Task 2.4 — Month-by-month trend (4 marks)
# With a CTE named monthly (month = SUBSTR(appt_date,1,7)), compute appointments and no_show_pct per month,
# then use LAG() with OVER (ORDER BY month) to show the change in percentage points
# this month's rate minus the previous month's rate (blank for January).

 # Solution
 # ==========================================
 # CARELOOP CLINICS
 # PART 2 - TASK 2.4
 # Month-by-month trend
 # ==========================================

import pandas as pd

# Step 1: Load cleaned appointment dataset
df = pd.read_csv("appointments_clean.csv")

# Step 2: Convert columns into correct formats
df["no_show"] = pd.to_numeric(
    df["no_show"], errors="coerce"
)

df["appt_date"] = df["appt_date"].astype(str)

# Step 3: Extract month from appointment date
df["month"] = df["appt_date"].str[:7]

# Step 4: Group appointments month by month
monthly = df.groupby("month").agg(
    appointments=("no_show", "count"),
    no_shows=("no_show", "sum")
).reset_index()

# Step 5: Calculate monthly no-show percentage
monthly["no_show_pct"] = (
    monthly["no_shows"] /
    monthly["appointments"] * 100
).round(1)

# Step 6: Calculate change from previous month
monthly["change_pp"] = (
    monthly["no_show_pct"].diff().round(1)
)

# Step 7: Display results
print("MONTH-BY-MONTH TREND")

print(
    monthly[
        ["month", "appointments", "no_show_pct", "change_pp"]
    ].to_string(index=False, na_rep="")
)

# Step 8: Display total appointments
print("\nTOTAL APPOINTMENTS:",
      monthly["appointments"].sum())

print("TOTAL NO-SHOWS:",
      monthly["no_shows"].sum())