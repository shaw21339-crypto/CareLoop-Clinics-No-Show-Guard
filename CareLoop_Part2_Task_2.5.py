# Task 2.5 — Rank clinics inside each city (5 marks)
# With a CTE clinic_rates (clinic, city, no_show_pct), select every clinic with RANK() OVER
# (PARTITION BY city ORDER BY no_show_pct DESC) as rank_in_city, plus a column
# vs_overall that says 'above', 'below' or 'equal' (no clinic is exactly equal here, but the query
# should handle it) by comparing the clinic's rate with the overall no-show
#  rate computed in a scalar subquery. Order by city, then rank.

#  Solution
# ==========================================
#  CARELOOP CLINICS
#  PART 2 - TASK 2.5
#  Rank clinics inside each city
#  ==========================================
import pandas as pd

# Step 1: Load the datasets
appointments = pd.read_csv("appointments_clean.csv")
clinics = pd.read_csv("clinics.csv")

# Step 2: Convert no_show into numeric format
appointments["no_show"] = pd.to_numeric(
    appointments["no_show"], errors="coerce"
)

# Step 3: Remove rows with missing required values
appointments = appointments.dropna(
    subset=["clinic_id", "no_show"]
)

# Step 4: Calculate clinic-wise statistics
clinic_rates = appointments.groupby("clinic_id").agg(
    appointments=("no_show", "count"),
    no_shows=("no_show", "sum")
).reset_index()

# Step 5: Calculate no-show percentage
clinic_rates["no_show_pct"] = (
    clinic_rates["no_shows"] /
    clinic_rates["appointments"] * 100
).round(1)

# Step 6: Add clinic name and city
clinic_rates = clinic_rates.merge(
    clinics[["clinic_id", "clinic_name", "city"]],
    on="clinic_id",
    how="inner"
)

# Step 7: Calculate overall no-show rate
overall_rate = (
    appointments["no_show"].sum() /
    len(appointments) * 100
)

# Step 8: Rank clinics inside each city
clinic_rates["rank_in_city"] = (
    clinic_rates.groupby("city")["no_show_pct"]
    .rank(method="min", ascending=False)
    .astype(int)
)

# Step 9: Compare with overall no-show rate
def compare_rate(rate):
    if rate > overall_rate:
        return "above"
    elif rate < overall_rate:
        return "below"
    else:
        return "equal"


clinic_rates["vs_overall"] = (
    clinic_rates["no_show_pct"].apply(compare_rate)
)

# Step 10: Sort results by city and rank
result = clinic_rates.sort_values(
    ["city", "rank_in_city"]
)

# Step 11: Display final results
print("CLINIC RANKING INSIDE EACH CITY")

print(
    result[
        [
            "clinic_name",
            "city",
            "no_show_pct",
            "rank_in_city",
            "vs_overall"
        ]
    ].to_string(index=False)
)

# Step 12: Display overall rate
print("\nOVERALL NO-SHOW RATE:",
      round(overall_rate, 2), "%")