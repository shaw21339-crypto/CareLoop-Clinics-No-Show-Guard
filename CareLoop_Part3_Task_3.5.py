# Task 3.5 — Tune, choose the model and the threshold, then test once (8 marks)
# (a) Run GridSearchCV(RandomForestClassifier(random_state=42), {"n_estimators": [100, 200], "max_depth":
# [3, 5, 8]}, cv=5, scoring="roc_auc") on the training set; print best_params_ and best_score_
# (a cross-validated ROC-AUC). (b) Choose the final model without touching the test set: compute the
# 5-fold cross-validated ROC-AUC on the training set for logistic regression, the depth-3 tree and the
# random forest — cross_val_score(model, X_train, y_train, cv=5, scoring="roc_auc").mean() — and compare
# them with the tuned forest('s best_score_. For logistic regression, give cross_val_score the unscaled'
# ' X_train together with the supplied pipeline below, so that the scaler is re-fitted on each fold')s
# own training part (scaling the whole training set first would let each validation fold influence the scaler). The highest wins. (c) Choose the threshold without touching the test set: get out-of-fold training probabilities for the winner with cross_val_predict(model, X_train, y_train, cv=5, method="predict_proba")[:, 1] (for logistic regression use the pipeline and the unscaled X_train) and compare thresholds 0.5 and 0.35 on precision, recall, F1 and number flagged; pick the threshold with the higher F1 and say why recall matters here (a missed warning costs an empty slot, an extra call costs a minute). (d) Fit the winner on the training set (the pipeline fits its own scaler) and evaluate it once on the test set at your chosen threshold: precision, recall, number flagged and ROC-AUC. (e) Save test_risk_scores.csv with columns appointment_id, no_show, risk_prob, flag (1 if risk_prob ≥ your threshold) for every test row. (To get appointment_id, keep it aside before building X, or use X_test.index to look it up in the loaded DataFrame.) In one sentence, say how a clinic would really choose the threshold: by how many follow-up calls the front desk can make in an evening, against the cost of an empty slot.
#
# Supplied pipeline for logistic regression (a pipeline chains the same fit/transform steps you used in
# 3.2 and repeats them inside every fold; the idea is the one from 20.2, the code is given because it was
# not shown in class):
#
# from sklearn.pipeline import Pipeline
# lr_pipe = Pipeline([("scaler", StandardScaler()), ("model", LogisticRegression(max_iter=1000))])
# cv_auc = cross_val_score(lr_pipe, X_train, y_train, cv=5, scoring="roc_auc").mean()
# oof = cross_val_predict(lr_pipe, X_train, y_train, cv=5, method="predict_proba")[:, 1]
# lr_pipe.fit(X_train, y_train)
# probs = lr_pipe.predict_proba(X_test)[:, 1]

# Solution
# ==========================================
# CARELOOP CLINICS
# PART 3 - TASK 3.5
# Tune, choose the model and the threshold, then test once
# ==========================================

import pandas as pd
import numpy as np

from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    cross_val_score,
    cross_val_predict
)

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
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

# 6. Split dataset using exactly the same settings
# as Tasks 3.1 to 3.4
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))


# ---------------------------------------------
# PART A: RANDOM FOREST GRID SEARCH
# ---------------------------------------------

print("\n========== PART A: GRID SEARCH ==========")

rf_grid = GridSearchCV(
    RandomForestClassifier(random_state=42),
    {
        "n_estimators": [100, 200],
        "max_depth": [3, 5, 8]
    },
    cv=5,
    scoring="roc_auc"
)

# Use training data only
rf_grid.fit(X_train, y_train)

print("Best parameters:", rf_grid.best_params_)
print("Best cross-validation ROC-AUC:",
      round(rf_grid.best_score_, 4))


# ---------------------------------------------
# PART B: COMPARE FOUR MODEL CANDIDATES
# ---------------------------------------------

print("\n========== PART B: MODEL SELECTION ==========")

# Logistic Regression pipeline
# Scaler is fitted separately inside each CV fold
lr_pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=1000))
])

# Decision Tree with depth 3
tree_model = DecisionTreeClassifier(
    max_depth=3,
    random_state=42
)

# Random Forest with default settings from Task 3.4
rf_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Tuned Random Forest from GridSearchCV
tuned_rf = rf_grid.best_estimator_

# Calculate 5-fold CV ROC-AUC on training data only
lr_cv_auc = cross_val_score(
    lr_pipe,
    X_train,
    y_train,
    cv=5,
    scoring="roc_auc"
).mean()

tree_cv_auc = cross_val_score(
    tree_model,
    X_train,
    y_train,
    cv=5,
    scoring="roc_auc"
).mean()

rf_cv_auc = cross_val_score(
    rf_model,
    X_train,
    y_train,
    cv=5,
    scoring="roc_auc"
).mean()

tuned_rf_cv_auc = rf_grid.best_score_

# Store model names and CV scores
cv_results = pd.DataFrame({
    "Model": [
        "Logistic Regression Pipeline",
        "Decision Tree (Depth 3)",
        "Random Forest (100 trees)",
        "Tuned Random Forest"
    ],
    "CV ROC-AUC": [
        lr_cv_auc,
        tree_cv_auc,
        rf_cv_auc,
        tuned_rf_cv_auc
    ]
})

print("\nCross-validation comparison:")
print(cv_results.round(4).to_string(index=False))

# Select the highest CV ROC-AUC
models = {
    "Logistic Regression Pipeline": lr_pipe,
    "Decision Tree (Depth 3)": tree_model,
    "Random Forest (100 trees)": rf_model,
    "Tuned Random Forest": tuned_rf
}

best_model_name = cv_results.loc[
    cv_results["CV ROC-AUC"].idxmax(),
    "Model"
]

winner = models[best_model_name]

print("\nSelected model:", best_model_name)
print(
    "Highest training CV ROC-AUC:",
    round(cv_results["CV ROC-AUC"].max(), 4)
)


# ---------------------------------------------
# PART C: CHOOSE THRESHOLD USING OOF PROBABILITIES
# ---------------------------------------------

print("\n========== PART C: THRESHOLD SELECTION ==========")

# Generate out-of-fold probabilities using training data only
oof_prob = cross_val_predict(
    winner,
    X_train,
    y_train,
    cv=5,
    method="predict_proba"
)[:, 1]

threshold_results = []

for threshold in [0.50, 0.35]:

    oof_pred = (oof_prob >= threshold).astype(int)

    precision = precision_score(
        y_train,
        oof_pred,
        zero_division=0
    )

    recall = recall_score(
        y_train,
        oof_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_train,
        oof_pred,
        zero_division=0
    )

    number_flagged = int(oof_pred.sum())

    threshold_results.append({
        "Threshold": threshold,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "Number Flagged": number_flagged
    })

threshold_table = pd.DataFrame(threshold_results)

print("\nOut-of-fold threshold comparison:")
print(threshold_table.round(4).to_string(index=False))

# Select threshold with higher F1
# If F1 values tie, this selects 0.50
best_threshold_row = threshold_table.loc[
    threshold_table["F1"].idxmax()
]

chosen_threshold = float(
    best_threshold_row["Threshold"]
)

print("\nChosen threshold:", chosen_threshold)
print("Reason: It has the higher out-of-fold F1 score.")

print(
    "Recall matters because a missed no-show warning can leave "
    "a clinic appointment slot empty, while an extra phone call "
    "costs staff time."
)


# ---------------------------------------------
# PART D: FIT WINNER AND TEST ONCE
# ---------------------------------------------

print("\n========== PART D: FINAL TEST EVALUATION ==========")

# Fit the winning model on the full training set
winner.fit(X_train, y_train)

# Get test probabilities
test_prob = winner.predict_proba(X_test)[:, 1]

# Apply the selected threshold
test_pred = (test_prob >= chosen_threshold).astype(int)

# Calculate final test metrics
test_precision = precision_score(
    y_test,
    test_pred,
    zero_division=0
)

test_recall = recall_score(
    y_test,
    test_pred,
    zero_division=0
)

test_auc = roc_auc_score(
    y_test,
    test_prob
)

number_flagged_test = int(test_pred.sum())

print("Final model:", best_model_name)
print("Chosen threshold:", chosen_threshold)
print("Test precision:", round(test_precision, 4))
print("Test recall:", round(test_recall, 4))
print("Test number flagged:", number_flagged_test)
print("Test ROC-AUC:", round(test_auc, 4))


# ---------------------------------------------
# PART E: SAVE TEST RISK SCORES
# ---------------------------------------------

print("\n========== PART E: SAVE RISK SCORES ==========")

# Use original row indices to recover appointment IDs.
# X_test retains the original DataFrame indices.
test_risk_scores = pd.DataFrame({
    "appointment_id": df.loc[X_test.index, "appointment_id"].values,
    "no_show": y_test.values,
    "risk_prob": test_prob,
    "flag": test_pred
})

output_path = (
    Path(__file__).resolve().parent / "test_risk_scores.csv"
)

test_risk_scores.to_csv(
    output_path,
    index=False
)

print("Risk score file saved successfully!")
print("File location:", output_path)

print("\nFirst five risk scores:")
print(test_risk_scores.head().to_string(index=False))


# ---------------------------------------------
# FINAL CONCLUSION
# ---------------------------------------------

print("\n========== TASK 3.5 CONCLUSION ==========")

print(
    "The final model was selected using training-set "
    "cross-validation ROC-AUC, and the threshold was selected "
    "using out-of-fold training probabilities."
)

print(
    "In practice, a clinic would choose the threshold based on "
    "how many follow-up calls the front desk can make in an "
    "evening, balanced against the cost of an empty appointment slot."
)

print("\nTask 3.5 completed successfully.")