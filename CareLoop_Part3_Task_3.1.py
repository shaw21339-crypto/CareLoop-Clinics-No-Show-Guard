# Part 3 — Machine Learning: predict no-shows and choose the model honestly (30 marks)
# Load Part 1('s appointments_clean.csv. The goal is a model whose risk score the front desk can use, the '
# 'evening before, to decide whom to phone. Only about 1 booking in 5 is a no-show, so judge '
# 'every model by recall, precision and ROC-AUC as well as accuracy. Rule for the whole Part:'
# 'the test set is for reporting only — never use it to choose a model, a setting or a threshold.'
# ' Two honest limits to remember (you will state them in Task 4.4): the medians, quartiles and '
# 'outlier fences in Task 1.3 were calculated on all 990 rows before the split, so the test rows'
#  ' had a small indirect influence on the cleaning (in a real system they would be calculated on'
#  ' the training rows only); the same patient can appear in several bookings, so a random split '
#  'can put one patient in both train and test; and the split is random, whereas a real system'
#  ' would be trained on the past and used on the future.)

# Task 3.1 — Features, split and baseline (5 marks)
# Build X from age, distance_km, fee_inr, lead_days, prior_no_shows, reminder_sent
# (convert Yes/No to 1/0 with .map), and the one-hot encoded booking_channel and visit_type (pd.get_dummies
# (X, columns=["booking_channel","visit_type"])).
# Do not use patient_id, appointment_id, dates, clinic_id, gender or status as features. Target y = no_show.
# Split with train_test_split(X, y, test_size=0.2, random_state=42). Report the training and test sizes,
# the number of no-shows in the test set, and the baseline accuracy of always predicting "Attended".
# Do not shuffle or re-sort the rows after loading appointments_clean.csv: the exact test-set counts below
# depend on the row order of that file.

# Solution
# ==========================================
# CARELOOP CLINICS
# PART 3 - TASK 3.1
# Features, Split and Baseline
# ==========================================

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from pathlib import Path

# 1. Load the cleaned CSV file
file_path = Path(__file__).resolve().parent / "appointments_clean.csv"

df = pd.read_csv(file_path)

print("File loaded successfully!")
print("Total rows:", len(df))

# 2. Check required columns
required_columns = [
    "age",
    "distance_km",
    "fee_inr",
    "lead_days",
    "prior_no_shows",
    "reminder_sent",
    "booking_channel",
    "visit_type",
    "no_show"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# 3. Create feature dataset X
X = df[
    [
        "age",
        "distance_km",
        "fee_inr",
        "lead_days",
        "prior_no_shows",
        "reminder_sent",
        "booking_channel",
        "visit_type"
    ]
].copy()

# 4. Convert reminder_sent Yes/No into 1/0
X["reminder_sent"] = (
    X["reminder_sent"]
    .astype(str)
    .str.strip()
    .map({"Yes": 1, "No": 0})
)

if X["reminder_sent"].isna().any():
    raise ValueError("reminder_sent contains values other than Yes/No.")

# 5. One-hot encode booking_channel and visit_type
X = pd.get_dummies(
    X,
    columns=["booking_channel", "visit_type"],
    dtype=int
)

# 6. Create target variable
y = df["no_show"].copy()

# Convert Yes/No target into 1/0 if necessary
if y.dtype == "object":
    y = y.astype(str).str.strip().map({"Yes": 1, "No": 0})

if y.isna().any():
    raise ValueError("no_show contains missing or unexpected values.")

y = y.astype(int)

# 7. Split data into training and test sets
# Do not sort or shuffle the original dataframe before this step.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# 8. Calculate baseline accuracy
# Baseline always predicts Attended (0)
baseline_predictions = [0] * len(y_test)

baseline_accuracy = accuracy_score(
    y_test,
    baseline_predictions
)

# 9. Display results
print("\n========== TASK 3.1 RESULTS ==========")

print("Total dataset rows:", len(df))
print("Training set size:", len(X_train))
print("Test set size:", len(X_test))

print("No-shows in test set:", int(y_test.sum()))

print(
    "Baseline accuracy (always predicting Attended):",
    round(baseline_accuracy, 4)
)

print("\nFeature columns:")
print(list(X.columns))

print("\nTask 3.1 completed successfully.")