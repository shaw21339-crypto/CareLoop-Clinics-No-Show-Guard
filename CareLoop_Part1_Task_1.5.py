# Task 1.5 — Enrich the clinics from a live API (3 marks)

# For each of the 8 clinics call the free Open-Meteo API with requests.get
#     ("https://api.open-meteo.com/v1/forecast", params={"latitude": ..., "longitude": ..., "hourly":
#     "temperature_2m",  "forecast_days": 1}). Check status_code == 200 before using the reply, read the JSON,
#     take the first value of ["hourly"]["temperature_2m"] (the midnight-UTC reading, a stand-in rather than
#     the current  weather) as temp_c, and save clinics_enriched.csv (the original columns plus temp_c;
#     df.to_csv("file.csv", index=False) writes a DataFrame to CSV). No API key is needed.
#     If the API fails: pass timeout=10 to requests.get, wrap the call in try/except requests.exceptions.
#     RequestException, retry that clinic once, and if it still fails (or the status is not 200, or hourly is
#     missing) store None as temp_c, print the clinic('s name and the reason, and carry on. Never type in a '
#     'made-up temperature; in load_data.sql a missing value is written as NULL (unquoted).)

# Solution

# ==========================================
# CARELOOP CLINICS
# PART 1 - TASK 1.5
# Enrich the clinics from a live API
# ==========================================

import pandas as pd
import requests
from pathlib import Path
import time

# ==========================================
# STEP 1: FIND THE CLINIC CSV FILE
# ==========================================

folder = Path(__file__).resolve().parent

print("========== TASK 1.5 ==========")
print("Searching for clinic CSV file...")

# Possible column names
name_options = [
    "clinic_name", "clinic", "name", "clinic_id"
]

lat_options = [
    "latitude", "lat"
]

lon_options = [
    "longitude", "lon", "lng"
]

# Search CSV files in the project folder
csv_files = [
    p for p in folder.glob("*.csv")
    if p.name.lower() != "clinics_enriched.csv"
    and p.name.lower() != "appointments.csv"
]

clinic_file = None
df = None
name_col = None
lat_col = None
lon_col = None

for file in csv_files:

    try:
        temp_df = pd.read_csv(file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            temp_df = pd.read_csv(file, encoding="cp1252")
        except Exception:
            continue
    except Exception:
        continue

    # Match column names without case or space differences
    column_map = {
        str(col).strip().lower(): col
        for col in temp_df.columns
    }

    found_name = next(
        (column_map[c] for c in name_options
         if c in column_map), None
    )

    found_lat = next(
        (column_map[c] for c in lat_options
         if c in column_map), None
    )

    found_lon = next(
        (column_map[c] for c in lon_options
         if c in column_map), None
    )

    if found_name and found_lat and found_lon:
        if len(temp_df) == 8:
            clinic_file = file
            df = temp_df
            name_col = found_name
            lat_col = found_lat
            lon_col = found_lon
            break

if df is None:
    print("\nClinic CSV not found automatically.")
    print("CSV files found:")

    for file in csv_files:
        print("-", file.name)

    raise FileNotFoundError(
        "No CSV with 8 clinics and name, latitude, "
        "longitude columns was found. Check your clinic CSV."
    )

print("Clinic file found:", clinic_file.name)
print("Total clinics:", len(df))
print("Columns:", df.columns.tolist())


# ==========================================
# STEP 2: SET OPEN-METEO API
# ==========================================

API_URL = "https://api.open-meteo.com/v1/forecast"

temperatures = []


# ==========================================
# STEP 3: CREATE API FUNCTION
# ==========================================

def get_temperature(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "forecast_days": 1,
        "timezone": "GMT"
    }

    # Two attempts: original request + one retry
    for attempt in range(2):

        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            temperature = data["hourly"]["temperature_2m"][0]

            if temperature is None:
                raise ValueError(
                    "Temperature value is missing"
                )

            return temperature

        except (
            requests.exceptions.RequestException,
            KeyError,
            IndexError,
            TypeError,
            ValueError
        ) as error:

            if attempt == 0:
                print("Request failed. Retrying...")
                time.sleep(1)

            else:
                print("API failed:", error)

    return None


# ==========================================
# STEP 4: PROCESS ALL 8 CLINICS
# ==========================================

print("\n========== PROCESSING CLINICS ==========")

for index, row in df.iterrows():

    clinic_name = row[name_col]

    print("\nClinic:", clinic_name)

    try:
        latitude = float(row[lat_col])
        longitude = float(row[lon_col])

        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid latitude")

        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid longitude")

        temperature = get_temperature(
            latitude,
            longitude
        )

    except (ValueError, TypeError) as error:

        temperature = None

        print("Clinic coordinate error:", error)

    if temperature is None:
        print("Temperature unavailable for:", clinic_name)
    else:
        print("Temperature:", temperature, "°C")

    temperatures.append(temperature)


# ==========================================
# STEP 5: ADD temp_c COLUMN
# ==========================================

df["temp_c"] = temperatures

print("\n========== ENRICHED CLINIC DATA ==========")

print(df)


# ==========================================
# STEP 6: SAVE ENRICHED CSV
# ==========================================

output_file = folder / "clinics_enriched.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)


# ==========================================
# STEP 7: FINAL RESULTS
# ==========================================

print("\n========== FINAL RESULTS ==========")

print("Total clinics:", len(df))

print(
    "Successful API results:",
    df["temp_c"].notna().sum()
)

print(
    "Missing temperatures:",
    df["temp_c"].isna().sum()
)

print("Output file:", output_file)

print("\nTask 1.5 completed successfully!")