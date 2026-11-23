# Task 3.4 — Random forest and a comparison table (6 marks)
# Fit RandomForestClassifier(n_estimators=100, random_state=42). Report accuracy, recall and ROC-AUC
# (use predict_proba(X_test)[:, 1] for AUC) and the top three rf.feature_importances_ (the attribute name
# is given because the course mentioned the idea only briefly). Then build a table with one row each for
# logistic regression, the depth-3 tree and the random forest (accuracy, recall, ROC-AUC) and say which model
# looks best and why; this table is for reporting — the formal choice is made in Task 3.5.

# Solution

# ==========================================
# CARELOOP CLINICS
# PART 3 - TASK 3.4
# Random forest and a comparison table
# ==========================================

import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    recall_score,
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

# 3. Convert reminder_sent Yes/No into 1/0
X["reminder_sent"] = (
    X["reminder_sent"]
    .astype(str)
    .str.strip()
    .map({"Yes": 1, "No": 0})
)

if X["reminder_sent"].isna().any():
    raise ValueError("Unexpected value in reminder_sent.")

# 4. One-hot encode categorical columns
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

# 6. Split dataset (same as Tasks 3.1, 3.2 and 3.3)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))

# -----------------------------------------
# MODEL 1: LOGISTIC REGRESSION
# -----------------------------------------

# Scale only for Logistic Regression
scaler = StandardScaler()

X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

logistic_model = LogisticRegression(max_iter=1000)

logistic_model.fit(X_train_s, y_train)

logistic_pred = logistic_model.predict(X_test_s)
logistic_prob = logistic_model.predict_proba(X_test_s)[:, 1]

logistic_accuracy = accuracy_score(y_test, logistic_pred)
logistic_recall = recall_score(
    y_test, logistic_pred, zero_division=0
)
logistic_auc = roc_auc_score(y_test, logistic_prob)

# -----------------------------------------
# MODEL 2: DECISION TREE (MAX_DEPTH=3)
# -----------------------------------------

tree_model = DecisionTreeClassifier(
    max_depth=3,
    random_state=42
)

tree_model.fit(X_train, y_train)

tree_pred = tree_model.predict(X_test)
tree_prob = tree_model.predict_proba(X_test)[:, 1]

tree_accuracy = accuracy_score(y_test, tree_pred)
tree_recall = recall_score(
    y_test, tree_pred, zero_division=0
)
tree_auc = roc_auc_score(y_test, tree_prob)

# -----------------------------------------
# MODEL 3: RANDOM FOREST
# -----------------------------------------

rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)

# Required probability for no-show class
rf_prob = rf.predict_proba(X_test)[:, 1]

rf_accuracy = accuracy_score(y_test, rf_pred)

rf_recall = recall_score(
    y_test, rf_pred, zero_division=0
)

rf_auc = roc_auc_score(y_test, rf_prob)

# -----------------------------------------
# RANDOM FOREST RESULTS
# -----------------------------------------

print("\n========== RANDOM FOREST RESULTS ==========")

print("Accuracy:", round(rf_accuracy, 4))
print("Recall:", round(rf_recall, 4))
print("ROC-AUC:", round(rf_auc, 4))

# -----------------------------------------
# TOP THREE FEATURE IMPORTANCES
# -----------------------------------------

print("\n========== TOP THREE IMPORTANT FEATURES ==========")

importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": rf.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

top_three = importance_df.head(3)

print(top_three.to_string(index=False))

# Save feature importance results
importance_df.to_csv(
    "random_forest_feature_importance.csv",
    index=False
)

# -----------------------------------------
# COMPARISON TABLE
# -----------------------------------------

comparison = pd.DataFrame({
    "Model": [
        "Logistic Regression",
        "Decision Tree (Depth 3)",
        "Random Forest"
    ],
    "Accuracy": [
        logistic_accuracy,
        tree_accuracy,
        rf_accuracy
    ],
    "Recall": [
        logistic_recall,
        tree_recall,
        rf_recall
    ],
    "ROC-AUC": [
        logistic_auc,
        tree_auc,
        rf_auc
    ]
})

print("\n========== MODEL COMPARISON TABLE ==========")

print(
    comparison.round(4).to_string(index=False)
)

# Save comparison table
comparison.to_csv(
    "model_comparison.csv",
    index=False
)

# -----------------------------------------
# REPORTING CONCLUSION
# -----------------------------------------

print("\n========== TASK 3.4 CONCLUSION ==========")

best_auc_model = comparison.loc[
    comparison["ROC-AUC"].idxmax(),
    "Model"
]

print(
    "Based on test ROC-AUC,",
    best_auc_model,
    "has the highest value in this comparison."
)

print(
    "Accuracy, recall and ROC-AUC should be considered together. "
    "The formal model choice will be made in Task 3.5."
)

print("\nTask 3.4 completed successfully.")