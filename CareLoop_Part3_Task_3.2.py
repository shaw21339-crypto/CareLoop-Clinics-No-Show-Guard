# Task 3.2 — Logistic regression (6 marks)
# Scale with StandardScaler (scaler = StandardScaler(), X_train_s = scaler.fit_transform(X_train),
# X_test_s = scaler.transform(X_test) — fit on the training set only), fit LogisticRegression(max_iter=1000),
# and report accuracy, the confusion matrix, precision, recall, F1 and ROC-AUC on the test set. Print the
# coefficients (model.coef_[0], one per feature, in the column order of X) next to the feature names and report
# np.exp(coefficient) for reminder_sent. Remember that the model was fitted on scaled features: to get the
# effect of a reminder going from No (0) to Yes (1), divide the coefficient by the feature('s standard '
# 'deviation (scaler.scale_) before applying np.exp. State both numbers and explain in one sentence why they'
# 'differ. Word your conclusion as an association ("in this model, holding the other features constant …"):'
# ' the data are observational, so it does not prove that reminders cause fewer no-shows.)

# Solution

# ==========================================
# CARELOOP CLINICS
# PART 3 - TASK 3.2
# LOGISTIC REGRESSION
# ==========================================

import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
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

# 3. Convert reminder_sent Yes/No to 1/0
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

# 6. Split data (same settings as Task 3.1)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))

# 7. Scale features
# Fit scaler ONLY on training data
scaler = StandardScaler()

X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# 8. Train Logistic Regression model
model = LogisticRegression(max_iter=1000)

model.fit(X_train_s, y_train)

# 9. Make test predictions
y_pred = model.predict(X_test_s)

# Predicted probability for no-show class (1)
y_prob = model.predict_proba(X_test_s)[:, 1]

# 10. Calculate evaluation metrics
accuracy = accuracy_score(y_test, y_pred)

cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

precision = precision_score(
    y_test, y_pred, zero_division=0
)

recall = recall_score(
    y_test, y_pred, zero_division=0
)

f1 = f1_score(
    y_test, y_pred, zero_division=0
)

roc_auc = roc_auc_score(y_test, y_prob)

# 11. Display evaluation results
print("\n========== MODEL EVALUATION ==========")

print("Accuracy:", round(accuracy, 4))
print("\nConfusion Matrix:")
print(cm)

print("\nPrecision:", round(precision, 4))
print("Recall:", round(recall, 4))
print("F1 Score:", round(f1, 4))
print("ROC-AUC:", round(roc_auc, 4))

# 12. Print coefficients next to feature names
print("\n========== FEATURE COEFFICIENTS ==========")

coefficients = model.coef_[0]

for feature_name, coefficient in zip(X.columns, coefficients):
    print(f"{feature_name}: {coefficient:.6f}")

# 13. Calculate reminder_sent effect
reminder_index = list(X.columns).index("reminder_sent")

reminder_coefficient = coefficients[reminder_index]

# Number 1: Exponential of scaled coefficient
scaled_odds_ratio = np.exp(reminder_coefficient)

# Number 2: Effect for a one-unit change in original reminder_sent
original_scale_coefficient = (
    reminder_coefficient / scaler.scale_[reminder_index]
)

original_scale_odds_ratio = np.exp(original_scale_coefficient)

print("\n========== REMINDER EFFECT ==========")

print(
    "Reminder coefficient (scaled):",
    round(reminder_coefficient, 6)
)

print(
    "np.exp(scaled coefficient):",
    round(scaled_odds_ratio, 6)
)

print(
    "Reminder coefficient on original scale:",
    round(original_scale_coefficient, 6)
)

print(
    "np.exp(original-scale coefficient):",
    round(original_scale_odds_ratio, 6)
)

# 14. Conclusion
print("\n========== CONCLUSION ==========")

if original_scale_odds_ratio < 1:
    print(
        "In this model, holding the other features constant, "
        "having a reminder sent is associated with lower odds of a no-show."
    )
elif original_scale_odds_ratio > 1:
    print(
        "In this model, holding the other features constant, "
        "having a reminder sent is associated with higher odds of a no-show."
    )
else:
    print(
        "In this model, holding the other features constant, "
        "reminder_sent is not associated with a change in the estimated odds."
    )

print(
    "This is an observational association and does not prove "
    "that reminders cause fewer or more no-shows."
)

print("\nTask 3.2 completed successfully.")