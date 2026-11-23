# Task 1.1 — Read the file the foundations way (5 marks)

# Using only the csv module (not pandas): open appointments.csv with with open(..., newline=""), read it
# with csv.DictReader, and print the header and row count. Write a function parse_row(row) that converts age,
# fee_inr and prior_no_shows to int and distance_km to float, returning the converted dictionary. Loop over
# every row; use try/except ValueError to put rows that fail into a rejected list and the rest into an
# accepted list. Save rejected with json.dump(..., indent=2) as rejected_rows.json.

# Solution

# ==========================================
# CARELOOP CLINICS
# PART 1 - TASK 1.1
# Read the file the foundations way
# ==========================================
# Step 1: Import the required modules
import csv
import json

# Explanation:
# csv reads CSV files.
# json saves rejected records in JSON format

# Step 2: Open and read the CSV file
# Understand this structure:

with open("appointments.csv", "r", newline="",
          encoding="utf-8") as file:

    reader = csv.DictReader(file)

    rows = list(reader)

    print("Headers:", reader.fieldnames)
    print("Total rows:", len(rows))

# Explanation:
#        Code                                              Meaning
#       open()                                       Opens the CSV file
#      newline=""                              Handles CSV newlines correctly
#     DictReader()                             Reads each row as a dictionary
#      list(reader)                                Stores all rows in a list
#      fieldnames                                     Displays column names
#       len(rows)                                         Counts records

# Step 3: Understand the parse_row(row) function
def parse_row(row):
    row["age"] =int(row["age"])
    return row

# Step 4: Separate accepted and rejected rows

accepted = []
rejected = []

for row in rows:

    try:
        converted_row = parse_row(row)
        accepted.append(converted_row)

    except ValueError:
        rejected.append(row)

# Step 5: Save rejected rows as JSON
with open("rejected_rows.json", "w",
          encoding="utf-8") as file:

    json.dump(rejected, file, indent=2)

# Step 6: Check  results

print("Accepted rows:", len(accepted))
print("Rejected rows:", len(rejected))
print("Total rows:", len(accepted) + len(rejected))

print("\nTask 1.1 completed successfully!")