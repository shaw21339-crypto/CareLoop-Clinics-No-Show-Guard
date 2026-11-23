# CareLoop Clinics - No-Show Guard

**GitHub Repository:** ADD_YOUR_GITHUB_REPOSITORY_LINK_HERE

## Project Overview

CareLoop Clinics - No-Show Guard is a data analysis and machine learning project
that studies missed medical appointments and explores how clinics can identify
patients who may need additional appointment reminders or follow-up support.

## Four-Part Project Summary

1. **Part 1 - Python and Data Foundations:** Processed 1,020 original appointment rows; 988 rows were accepted during the initial validation.
2. **Part 2 - SQL Analysis:** Gomti Nagar had 90 appointments and a 33.3% no-show rate.
3. **Part 3 - Machine Learning:** Logistic Regression achieved an ROC-AUC of 0.86, using a classification threshold of 0.50.
4. **Part 4 - Generative AI:** Analysed 10 follow-up notes; 5 matched appointments had no reminder recorded.

## Part 4: Root Cause and Reminder Analysis

The AI analysis results were merged with the cleaned appointment dataset using
`appointment_id`.

- Total AI analysis records: 10
- Matched appointment records: 10
- Unmatched records: 0
- Records without a reminder: 5
- Percentage without a reminder among matched records: 50.00%

### Root Cause vs Reminder Sent

| Root cause | No | Yes | All |
| --- | --- | --- | --- |
| cost_or_fee | 0 | 1 | 1 |
| distance_or_transport | 1 | 1 | 2 |
| forgot_on_no_reminder | 1 | 0 | 1 |
| other | 1 | 0 | 1 |
| work_or_schedule | 1 | 1 | 2 |
| All | 4 | 3 | 7 |

## Business Recommendation

CareLoop Clinics should use a combination of appointment reminders, targeted
follow-up, and risk-based patient outreach to reduce missed appointments.
The initial dataset contained 1,020 rows, of which 988 were accepted during
validation. In Part 2, Gomti Nagar recorded 90 appointments with a 33.3%
no-show rate, suggesting that clinic-level monitoring is useful. In Part 3,
Logistic Regression achieved an ROC-AUC of 0.86 at a classification
threshold of 0.50. In Part 4, 10 patient
notes were analysed and 5 matched appointments had no reminder
recorded. Clinics should review reminder delivery, monitor high-risk predictions,
and use staff follow-up where capacity permits. These findings are useful for
planning, but should not be treated as proof that reminders alone cause
attendance to improve.

## Machine Learning Model

**Selected model:** Logistic Regression

Logistic Regression was selected because it provides a straightforward
classification approach and produces probabilities that can help identify
patients who may miss appointments.

- ROC-AUC: 0.86
- Classification threshold: 0.50

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
