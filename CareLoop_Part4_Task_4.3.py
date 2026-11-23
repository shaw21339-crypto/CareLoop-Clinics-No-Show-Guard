# Task 4.3 — Break it on purpose (5 marks)

# (a) Feed the Pydantic model two deliberately bad replies and catch each with try/except ValidationError
# (from pydantic import ValidationError): one with confidence = 1.7, one missing recommended_action; print
# what each error says. (b) For notes N007 (Hinglish) and N009 (ambiguous), compare two prompts at
# temperature=0: V1 = just "Classify this note", V2 = your CRAFT prompt with the allowed values and the
# instruction to answer other rather than guess. Use the same schema and settings for both (root_cause as a
# plain string, JSON mode, temperature=0), so that the only difference is the prompt; then check each reply
# against the allowed list. Show the four results in a small table and say which prompt you would deploy.
# (c) Count and print the total number of API calls you used across Tasks 4.1–4.3
# (about 14 on a first pass: 1 in 4.1, 9 in 4.2, 4 here; 12 if you reuse your 4.2 results for the V2 prompt).

# Solution

# ==================================================
# CARELOOP CLINICS
# PART 4 - TASK 4.3
# Break it on purpose
# ==================================================
import os
import json
import time
import pandas as pd

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError


# ==========================================
# 1. GEMINI SETUP
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.5-flash-lite"

task_4_3_api_calls = 0


# ==========================================
# 2. PYDANTIC MODEL
# ==========================================

class FollowupInsight(BaseModel):
    root_cause: str = Field(min_length=3)
    confidence: float = Field(ge=0, le=1)
    summary: str = Field(min_length=5)
    recommended_action: str = Field(min_length=5)


ALLOWED_ROOT_CAUSES = [
    "forgot_on_no_reminder",
    "illness_or_emergency",
    "distance_or_transport",
    "cost_or_fee",
    "work_or_schedule",
    "other"
]


# ==========================================
# PART A: PYDANTIC VALIDATION TESTS
# ==========================================

print("\nPART A: PYDANTIC VALIDATION TESTS")
print("----------------------------------")

bad_reply_1 = {
    "root_cause": "other",
    "confidence": 1.7,
    "summary": "This is a test reply",
    "recommended_action": "Contact the patient"
}

bad_reply_2 = {
    "root_cause": "other",
    "confidence": 0.5,
    "summary": "This is a test reply"
}

bad_replies = [bad_reply_1, bad_reply_2]

for number, bad_reply in enumerate(bad_replies, start=1):

    try:
        FollowupInsight(**bad_reply)
        print(f"Bad reply {number}: Unexpectedly passed")

    except ValidationError as error:
        print(f"\nBad reply {number} validation error:")
        print(error)


# ==========================================
# PART B: PROMPT COMPARISON
# ==========================================

print("\n\nPART B: PROMPT COMPARISON")
print("----------------------------------")

# Read CSV
CSV_FILE = "followup_notes.csv"

if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(
        "followup_notes.csv not found in project folder"
    )

notes = pd.read_csv(CSV_FILE)

print("CSV columns:", list(notes.columns))

if "note_id" not in notes.columns:
    raise ValueError("note_id column not found")

if "note_text" not in notes.columns:
    raise ValueError("note_text column not found")


# Select N007 and N009
selected_notes = notes[
    notes["note_id"].astype(str).str.strip().isin(
        ["N007", "N009"]
    )
].copy()

selected_notes["note_id"] = (
    selected_notes["note_id"].astype(str).str.strip()
)

# Ensure both notes exist
found_ids = set(selected_notes["note_id"])

if not {"N007", "N009"}.issubset(found_ids):
    raise ValueError(
        f"N007 or N009 is missing. Found: {found_ids}"
    )

# Sort in the requested order
selected_notes["sort_order"] = (
    selected_notes["note_id"].map({"N007": 1, "N009": 2})
)

selected_notes = selected_notes.sort_values("sort_order")


# V1: Simple prompt
V1_PROMPT = "Classify this note"


# V2: CRAFT prompt
V2_PROMPT = """
Context:
You are analysing patient appointment follow-up notes
for CareLoop Clinics.

Role:
Act as a careful healthcare appointment data analyst.

Action:
Classify the main reason for the missed appointment.

Use only one of these root_cause values:
forgot_on_no_reminder,
illness_or_emergency,
distance_or_transport,
cost_or_fee,
work_or_schedule,
other.

If the note is ambiguous or unclear, choose "other"
rather than guessing.

Tone:
Be neutral, careful, and factual.

Format:
Return only valid JSON containing:
root_cause, confidence, summary, recommended_action.

The summary must contain at most 25 words.
"""


# Same JSON schema and settings for both prompts
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "root_cause": {"type": "STRING"},
        "confidence": {"type": "NUMBER"},
        "summary": {"type": "STRING"},
        "recommended_action": {"type": "STRING"}
    },
    "required": [
        "root_cause",
        "confidence",
        "summary",
        "recommended_action"
    ]
}


# Gemini API function
def classify_note(note_text, prompt):

    global task_4_3_api_calls

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt + "\n\nPatient note:\n" + note_text,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            max_output_tokens=1024
        )
    )

    task_4_3_api_calls += 1

    raw_text = response.text or ""

    return json.loads(raw_text)


# Store comparison results
comparison_results = []

# Process N007 and N009
for _, row in selected_notes.iterrows():

    note_id = row["note_id"]
    note_text = row["note_text"]

    if pd.isna(note_text) or str(note_text).strip() == "":
        print(f"\n{note_id} is blank. Cannot compare prompts.")
        continue

    note_text = str(note_text).strip()

    # Run V1 and V2
    for version, prompt in [
        ("V1", V1_PROMPT),
        ("V2", V2_PROMPT)
    ]:

        # Pause between API calls
        if task_4_3_api_calls > 0:
            time.sleep(13)

        print(f"\nProcessing {note_id} with {version}")

        try:
            result = classify_note(note_text, prompt)

            root_cause = result.get("root_cause", "")

            # Check allowed list
            if root_cause in ALLOWED_ROOT_CAUSES:
                allowed_status = "Allowed"
            else:
                allowed_status = "Not allowed"

            comparison_results.append({
                "note_id": note_id,
                "prompt": version,
                "root_cause": root_cause,
                "allowed_list_check": allowed_status
            })

            print("Model response:", result)

        except Exception as error:

            print("API or JSON error:", error)

            comparison_results.append({
                "note_id": note_id,
                "prompt": version,
                "root_cause": "ERROR",
                "allowed_list_check": "Error"
            })


# Display comparison table
print("\n\nFOUR PROMPT COMPARISON RESULTS")
print("----------------------------------")

comparison_table = pd.DataFrame(comparison_results)

print(comparison_table.to_string(index=False))


# ==========================================
# PART C: API CALL COUNT
# ==========================================

print("\n\nPART C: API CALL COUNT")
print("----------------------------------")

# Enter your actual completed API calls from Tasks 4.1 and 4.2.
task_4_1_calls = 1
task_4_2_calls = 9

task_4_3_calls = task_4_3_api_calls

total_api_calls = (
    task_4_1_calls
    + task_4_2_calls
    + task_4_3_calls
)

print("Task 4.1 API calls:", task_4_1_calls)
print("Task 4.2 API calls:", task_4_2_calls)
print("Task 4.3 API calls:", task_4_3_calls)

print("----------------------------------")
print("TOTAL API CALLS:", total_api_calls)


# ==========================================
# DEPLOYMENT DECISION
# ==========================================

print("\n\nDEPLOYMENT DECISION")
print("----------------------------------")

print(
    "I would deploy V2 because it uses clear CRAFT "
    "instructions, specifies the allowed root causes, "
    "and tells the model to choose other rather than "
    "guess when a note is ambiguous."
)

print("\n===================================")
print("TASK 4.3 COMPLETED SUCCESSFULLY")