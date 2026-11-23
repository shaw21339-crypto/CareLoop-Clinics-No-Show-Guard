# Task 3.3 — Decision tree and overfitting (5 marks)
# Fit DecisionTreeClassifier(random_state=42) with no depth limit, and again with max_depth=3. For each,
# report training accuracy and test accuracy, and state in one sentence what the gap shows.

# Solution

# ==========================================
# CARELOOP CLINICS
# PART 3 - TASK 3.3
# Decision tree and overfitting
# ==========================================

import pandas as pd

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# 1. Load cleaned dataset
file_path = Path(__file__).resolve().parent / "appointments_clean.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Total rows:", len(df))

# 2. Create features (X)
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

# 3. Convert reminder_sent Yes/No into 1/0
X["reminder_sent"] = (
    X["reminder_sent"]
    .astype(str)
    .str.strip()
    .map({"Yes": 1, "No": 0})
)

if X["reminder_sent"].isna().any():
    raise ValueError("Unexpected value in reminder_sent.")

# 4. One-hot encode categorical features
X = pd.get_dummies(
    X,
    columns=["booking_channel", "visit_type"],
    dtype=int
)

# 5. Create target variable
y = df["no_show"].copy()

if y.dtype == "object":
    y = y.astype(str).str.strip().map({"Yes": 1, "No": 0})

if y.isna().any():
    raise ValueError("Unexpected or missing values in no_show.")

y = y.astype(int)

# 6. Split dataset (same as Task 3.1)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))

# -----------------------------------------
# MODEL 1: UNRESTRICTED DECISION TREE
# -----------------------------------------

tree_unrestricted = DecisionTreeClassifier(
    random_state=42
)

tree_unrestricted.fit(X_train, y_train)

train_pred_unrestricted = tree_unrestricted.predict(X_train)
test_pred_unrestricted = tree_unrestricted.predict(X_test)

train_accuracy_unrestricted = accuracy_score(
    y_train,
    train_pred_unrestricted
)

test_accuracy_unrestricted = accuracy_score(
    y_test,
    test_pred_unrestricted
)

# -----------------------------------------
# MODEL 2: DECISION TREE WITH MAX_DEPTH=3
# -----------------------------------------

tree_depth3 = DecisionTreeClassifier(
    max_depth=3,
    random_state=42
)

tree_depth3.fit(X_train, y_train)

train_pred_depth3 = tree_depth3.predict(X_train)
test_pred_depth3 = tree_depth3.predict(X_test)

train_accuracy_depth3 = accuracy_score(
    y_train,
    train_pred_depth3
)

test_accuracy_depth3 = accuracy_score(
    y_test,
    test_pred_depth3
)

# -----------------------------------------
# DISPLAY RESULTS
# -----------------------------------------

print("\n========== TASK 3.3 RESULTS ==========")

print("\nMODEL 1: UNRESTRICTED DECISION TREE")

print(
    "Training accuracy:",
    round(train_accuracy_unrestricted, 4)
)

print(
    "Test accuracy:",
    round(test_accuracy_unrestricted, 4)
)

print("\nMODEL 2: DECISION TREE WITH MAX_DEPTH=3")

print(
    "Training accuracy:",
    round(train_accuracy_depth3, 4)
)

print(
    "Test accuracy:",
    round(test_accuracy_depth3, 4)
)

# -----------------------------------------
# COMPARE TRAIN-TEST ACCURACY GAPS
# -----------------------------------------

gap_unrestricted = (
    train_accuracy_unrestricted - test_accuracy_unrestricted
)

gap_depth3 = (
    train_accuracy_depth3 - test_accuracy_depth3
)

print("\n========== ACCURACY GAP ==========")

print(
    "Unrestricted tree gap:",
    round(gap_unrestricted, 4)
)

print(
    "Depth-3 tree gap:",
    round(gap_depth3, 4)
)

print("\n========== CONCLUSION ==========")

print(
    "A large gap between training and test accuracy suggests "
    "overfitting: the model performs better on training data "
    "than on unseen test data."
)

print("\nTask 3.3 completed successfully.")