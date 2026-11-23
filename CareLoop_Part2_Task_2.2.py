 # Solution
 # ==========================================
 # CARELOOP CLINICS
 # PART 2 - TASK 2.2
 # No-show rate by clinic
 # ==========================================
import pandas as pd

# Read the CSV files
appointments = pd.read_csv("appointments_clean.csv")
clinics = pd.read_csv("clinics_enriched.csv")

# Merge appointment and clinic information
df = appointments.merge(
    clinics[["clinic_id", "clinic_name", "city"]],
    on="clinic_id",
    how="left"
)

# Calculate clinic-wise appointment counts
result = df.groupby(
    ["clinic_id", "clinic_name", "city"]
).agg(
    appointments=("appointment_id", "count"),
    no_shows=("no_show", "sum")
).reset_index()

# Calculate no-show percentage
result["no_show_pct"] = (
    100 * result["no_shows"] / result["appointments"]
).round(1)

# Display clinics with at least 95 appointments
filtered = result[result["appointments"] >= 95]

filtered = filtered.sort_values(
    "no_show_pct", ascending=False
)

print("CLINICS WITH AT LEAST 95 APPOINTMENTS")
print(filtered.to_string(index=False))

# Display all 8 clinics
print("\nALL 8 CLINICS")

print(
    result.sort_values(
        by="no_show_pct",
        ascending=False
    ).to_string(index=False)
)