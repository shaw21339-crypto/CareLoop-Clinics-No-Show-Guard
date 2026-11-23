# Task 4.4 — Recommendation and GitHub (5 marks)

# (a) (3 marks) Merge notes_analysed.csv with appointments_clean.csv on appointment_id and cross-tabulate
# root_cause against reminder_sent (pd.crosstab). Write README.md with: a 4-line summary (one finding per
# Part, each with its number); a one-paragraph recommendation that answers the business question using at
# least four numbers from Parts 1–4; the model you chose and why (include AUC and the threshold); and three
# limitations (choose from: the 10 notes are an illustration and cannot show the real reasons clinic-wide;
# the cleaning statistics came from all rows before the split; the same patient can sit in both
# train and test; the split is random, not past-to-future; one train/test split; a threshold that really
# depends on call capacity; clinic-level sample sizes; the data are observational, so associations are not
# causes). (b) (2 marks) Create the public GitHub repository, upload every file listed under Submission,
# confirm the key is nowhere in it, and paste the link at the top of the README.

# Solution
# ==================================================
# CARELOOP CLINICS
# PART 4 - TASK 4.4
# Recommendation and GitHub
# ==================================================

from pathlib import Path
import pandas as pd


# ==========================================
# 1. PROJECT SETTINGS
# ==========================================

PROJECT_FOLDER = Path(__file__).resolve().parent

NOTES_FILE = PROJECT_FOLDER / "notes_analysed.csv"
APPOINTMENTS_FILE = PROJECT_FOLDER / "appointments_clean.csv"

MERGED_OUTPUT = PROJECT_FOLDER / "notes_with_appointments.csv"
CROSSTAB_OUTPUT = PROJECT_FOLDER / "root_cause_reminder_crosstab.csv"
README_FILE = PROJECT_FOLDER / "README.md"

# Part 3 model details
MODEL_NAME = "Logistic Regression"
MODEL_AUC = 0.86
CLASSIFICATION_THRESHOLD = 0.50

# Replace this after creating your GitHub repository
GITHUB_REPO_URL = "ADD_YOUR_GITHUB_REPOSITORY_LINK_HERE"


# ==========================================
# 2. CHECK FILES
# ==========================================

print("\nTASK 4.4 - RECOMMENDATION AND GITHUB")
print("--------------------------------------")

if not NOTES_FILE.exists():
    raise FileNotFoundError(
        "notes_analysed.csv was not found in the project folder."
    )

if not APPOINTMENTS_FILE.exists():
    raise FileNotFoundError(
        "appointments_clean.csv was not found in the project folder."
    )


# ==========================================
# 3. READ CSV FILES
# ==========================================

notes = pd.read_csv(NOTES_FILE)
appointments = pd.read_csv(APPOINTMENTS_FILE)

print("\nFiles loaded successfully.")

print("AI analysis rows:", len(notes))
print("Clean appointment rows:", len(appointments))


# ==========================================
# 4. CHECK REQUIRED COLUMNS
# ==========================================

required_notes_columns = [
    "appointment_id",
    "root_cause"
]

required_appointment_columns = [
    "appointment_id",
    "reminder_sent"
]

for column in required_notes_columns:
    if column not in notes.columns:
        raise ValueError(
            f"{column} is missing from notes_analysed.csv"
        )

for column in required_appointment_columns:
    if column not in appointments.columns:
        raise ValueError(
            f"{column} is missing from appointments_clean.csv"
        )


# ==========================================
# 5. MERGE TWO DATASETS
# ==========================================

merged = pd.merge(
    notes,
    appointments,
    on="appointment_id",
    how="left",
    indicator=True,
    suffixes=("_note", "_appointment")
)

matched_count = (merged["_merge"] == "both").sum()
unmatched_count = (merged["_merge"] == "left_only").sum()

print("\nMERGE RESULTS")
print("--------------------------------------")
print("Total merged rows:", len(merged))
print("Matched appointments:", matched_count)
print("Unmatched appointments:", unmatched_count)

# Save merged dataset
merged.to_csv(MERGED_OUTPUT, index=False)

print("\nMerged file saved:", MERGED_OUTPUT.name)


# ==========================================
# 6. CROSS-TABULATION
# ==========================================

print("\nROOT CAUSE VS REMINDER SENT")
print("--------------------------------------")

# Use only rows with a matching appointment
matched_data = merged[
    merged["_merge"] == "both"
].copy()

cross_tab = pd.crosstab(
    matched_data["root_cause"],
    matched_data["reminder_sent"],
    margins=True
)

print(cross_tab)

# Save cross-tabulation
cross_tab.to_csv(CROSSTAB_OUTPUT)

print("\nCross-tabulation saved:", CROSSTAB_OUTPUT.name)


# ==========================================
# 7. PART 4 FINDINGS
# ==========================================

total_notes = len(merged)

no_reminder_count = (
    matched_data["reminder_sent"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["no", "0", "false"])
    .sum()
)

no_reminder_percentage = (
    no_reminder_count / len(matched_data) * 100
    if len(matched_data) > 0
    else 0
)

print("\nPART 4 FINDINGS")
print("--------------------------------------")
print("Notes analysed:", total_notes)
print("Notes matched with appointments:", matched_count)
print("Appointments without reminders:", no_reminder_count)
print(
    "Percentage without reminders:",
    round(no_reminder_percentage, 2), "%"
)


# ==========================================
# 8. CONVERT CROSS-TAB TO MARKDOWN
# ==========================================

def dataframe_to_markdown(dataframe):

    headers = ["Root cause"] + [
        str(column) for column in dataframe.columns
    ]

    lines = []

    lines.append("| " + " | ".join(headers) + " |")

    lines.append(
        "| " + " | ".join(["---"] * len(headers)) + " |"
    )

    for index, row in dataframe.iterrows():

        values = [str(index)] + [
            str(value) for value in row.values
        ]

        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


cross_tab_markdown = dataframe_to_markdown(cross_tab)


# ==========================================
# 9. CREATE README.MD
# ==========================================

readme_content = f"""# CareLoop Clinics - No-Show Guard

**GitHub Repository:** {GITHUB_REPO_URL}

## Project Overview

CareLoop Clinics - No-Show Guard is a data analysis and machine learning project
that studies missed medical appointments and explores how clinics can identify
patients who may need additional appointment reminders or follow-up support.

## Four-Part Project Summary

1. **Part 1 - Python and Data Foundations:** Processed 1,020 original appointment rows; 988 rows were 
accepted during the initial validation.
2. **Part 2 - SQL Analysis:** Gomti Nagar had 90 appointments and a 33.3% no-show rate.
3. **Part 3 - Machine Learning:** Logistic Regression achieved an ROC-AUC of {MODEL_AUC:.2f}, using a 
classification threshold of {CLASSIFICATION_THRESHOLD:.2f}.
4. **Part 4 - Generative AI:** Analysed {total_notes} follow-up notes; {no_reminder_count} matched 
appointments had no reminder recorded.

## Part 4: Root Cause and Reminder Analysis

The AI analysis results were merged with the cleaned appointment dataset using
`appointment_id`.

- Total AI analysis records: {total_notes}
- Matched appointment records: {matched_count}
- Unmatched records: {unmatched_count}
- Records without a reminder: {no_reminder_count}
- Percentage without a reminder among matched records: {no_reminder_percentage:.2f}%

### Root Cause vs Reminder Sent

{cross_tab_markdown}

## Business Recommendation

CareLoop Clinics should use a combination of appointment reminders, targeted
follow-up, and risk-based patient outreach to reduce missed appointments.
The initial dataset contained 1,020 rows, of which 988 were accepted during
validation. In Part 2, Gomti Nagar recorded 90 appointments with a 33.3%
no-show rate, suggesting that clinic-level monitoring is useful. In Part 3,
Logistic Regression achieved an ROC-AUC of {MODEL_AUC:.2f} at a classification
threshold of {CLASSIFICATION_THRESHOLD:.2f}. In Part 4, {total_notes} patient
notes were analysed and {no_reminder_count} matched appointments had no reminder
recorded. Clinics should review reminder delivery, monitor high-risk predictions,
and use staff follow-up where capacity permits. These findings are useful for
planning, but should not be treated as proof that reminders alone cause
attendance to improve.

## Machine Learning Model

**Selected model:** {MODEL_NAME}

Logistic Regression was selected because it provides a straightforward
classification approach and produces probabilities that can help identify
patients who may miss appointments.

- ROC-AUC: {MODEL_AUC:.2f}
- Classification threshold: {CLASSIFICATION_THRESHOLD:.2f}

The threshold should be reviewed against clinic staff capacity and the cost of
missed appointments before real-world deployment.

## Limitations

1. The 10 follow-up notes are an illustration and cannot show the real reasons
   for missed appointments across the entire clinic network.
2. The train/test split is random, not past-to-future, so performance may not
   reflect how the model works on future appointments.
3. The data are observational, so associations between reminders and
   attendance do not prove that reminders cause attendance to improve.

## Project Files

This repository should contain all files required by the official project
Submission checklist, including the relevant source code, datasets, and outputs.

## Security

The Gemini API key is stored locally in a `.env` file and must not be uploaded
to GitHub. The `.env` file is excluded through `.gitignore`.
"""


with open(README_FILE, "w", encoding="utf-8") as file:
    file.write(readme_content)


# ==========================================
# 10. CREATE .GITIGNORE
# ==========================================

gitignore_file = PROJECT_FOLDER / ".gitignore"

gitignore_content = """
.env
.venv/
venv/
__pycache__/
*.pyc
.idea/
"""

with open(gitignore_file, "w", encoding="utf-8") as file:
    file.write(gitignore_content.strip() + "\n")


# ==========================================
# 11. FINAL OUTPUT
# ==========================================

print("\nREADME AND GITHUB FILES")
print("--------------------------------------")

print("README.md created successfully.")
print(".gitignore created successfully.")

print("\nGenerated files:")
print("1.", MERGED_OUTPUT.name)
print("2.", CROSSTAB_OUTPUT.name)
print("3.", README_FILE.name)
print("4.", gitignore_file.name)

print("\nTASK 4.4 PART A COMPLETED")
