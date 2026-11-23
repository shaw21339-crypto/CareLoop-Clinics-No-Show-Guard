# Task 4.2 — Validate and process the 10 notes (7 marks)

# (a) Define a Pydantic model FollowupInsight(BaseModel) with root_cause: str = Field(min_length=3),
# confidence: float = Field(ge=0, le=1), summary: str = Field(min_length=5),
# recommended_action: str = Field(min_length=5), and write a check that root_cause is in the allowed
# list. (b) Read followup_notes.csv with pandas and loop over the first 10 rows.
# Input validation: pandas reads a blank note as NaN (a float, which has no .strip()),
# so test pd.isna(note_text) first, then str(note_text).strip() == "". If the note is missing, empty or only
# spaces, do not call the API — record root_cause="other", confidence=0.0, summary="No note recorded",
# recommended_action="Re-call patient" and validation_status="skipped_blank". Otherwise call analyse_note,
# validate the result with the Pydantic model (as in class: pass the dictionary into the class,
# FollowupInsight(**data)) and the allowed-list check, and set validation_status to "valid" or "invalid"
# (never let one bad reply stop the loop: use try/except). (c) Pause between calls (import time then time.
#  sleep(13)) to respect the free-tier rate limit. (d) Save notes_analysed.csv with columns note_id,
# appointment_id, root_cause, confidence, summary, recommended_action, validation_status, raw_response.
# Keep every reply, including invalid ones, and never repair it:
# put the model('s reply exactly as returned (the JSON text) in raw_response, copy whichever fields it did'
# ' contain, ''and leave a field empty if the reply lacked it
# (for a skipped blank note, raw_response is empty).

# Solution

# ==================================================
# CARELOOP CLINICS
# PART 4 - TASK 4.2
# VALIDATE AND PROCESS THE 10 NOTES
# ==================================================

import os
import json
import time
import pandas as pd

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


# =====================================================
# TASK 4.1 - GEMINI NOTE ANALYSIS
# =====================================================

# STEP 1: Load API key

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")


# STEP 2: Create Gemini client

client = genai.Client(api_key=API_KEY)


# STEP 3: Select Gemini model

MODEL_NAME = "gemini-3.5-flash-lite"


# STEP 4: Define JSON response schema

response_schema = {
    "type": "OBJECT",
    "properties": {
        "root_cause": {
            "type": "STRING"
        },
        "confidence": {
            "type": "NUMBER"
        },
        "summary": {
            "type": "STRING"
        },
        "recommended_action": {
            "type": "STRING"
        }
    },
    "required": [
        "root_cause",
        "confidence",
        "summary",
        "recommended_action"
    ]
}


# STEP 5: Define system instruction

SYSTEM_TEXT = """
You are a healthcare administration data analyst
working for CareLoop Clinics.

Analyse patient appointment follow-up notes.
Return accurate, professional and neutral results.
Do not invent information that is not present in the note.
Follow the requested JSON response format exactly.
"""


# STEP 6: Build CRAFT prompt

def build_prompt(note_text):

    prompt = f"""
    Context:
    CareLoop Clinics wants to understand why patients
    miss their scheduled appointments.

    Role:
    You are an experienced healthcare administration
    data analyst.

    Action:
    Analyse the patient follow-up note.
    Identify the main root cause, estimate confidence,
    write a summary of at most 25 words, and recommend
    an appropriate administrative action.

    Allowed root_cause values:
    - forgot_on_no_reminder
    - illness_or_emergency
    - distance_or_transport
    - cost_or_fee
    - work_or_schedule
    - other

    Root cause must be a plain string, not an enum.
    Use one of the allowed values above.

    Tone:
    Professional, neutral and concise.

    Format:
    Return valid JSON with exactly four fields:
    root_cause, confidence, summary, recommended_action.

    Confidence must be a number between 0 and 1.
    Summary must contain at most 25 words.

    Patient follow-up note:
    {note_text}
    """

    return prompt


# STEP 7: Define analyse_note function

def analyse_note(note_text, return_raw=False):

    prompt = build_prompt(note_text)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_TEXT,
            temperature=0,
            response_mime_type="application/json",
            response_schema=response_schema,
            max_output_tokens=1024
        )
    )

    # Preserve original Gemini response
    raw_text = response.text or ""

    # Convert JSON into Python dictionary
    try:
        result = json.loads(raw_text)

    except json.JSONDecodeError:
        if return_raw:
            return None, raw_text
        raise

    if return_raw:
        return result, raw_text

    return result


# =====================================================
# TASK 4.2 - VALIDATE AND PROCESS 10 NOTES
# =====================================================


# STEP 8: Define allowed root causes

ALLOWED_ROOT_CAUSES = [
    "forgot_on_no_reminder",
    "illness_or_emergency",
    "distance_or_transport",
    "cost_or_fee",
    "work_or_schedule",
    "other"
]


# STEP 9: Define Pydantic model

class FollowupInsight(BaseModel):

    root_cause: str = Field(min_length=3)

    confidence: float = Field(ge=0, le=1)

    summary: str = Field(min_length=5)

    recommended_action: str = Field(min_length=5)


# STEP 10: Read CSV file

notes = pd.read_csv("followup_notes.csv")

# Select first 10 rows

first_10_notes = notes.head(10)

# Store output results

results = []

# Count Gemini API calls

api_calls = 0


# STEP 11: Process each note

for index, row in first_10_notes.iterrows():

    note_id = row["note_id"]
    appointment_id = row["appointment_id"]
    note_text = row["note_text"]

    print("\n-----------------------------------")
    print("Processing NOTE ID:", note_id)

    # Create default result dictionary

    result_row = {
        "note_id": note_id,
        "appointment_id": appointment_id,
        "root_cause": "",
        "confidence": "",
        "summary": "",
        "recommended_action": "",
        "validation_status": "",
        "raw_response": ""
    }

    # STEP 12: Check blank notes

    if pd.isna(note_text) or str(note_text).strip() == "":

        result_row["root_cause"] = "other"
        result_row["confidence"] = 0.0
        result_row["summary"] = "No note recorded"
        result_row["recommended_action"] = "Re-call patient"
        result_row["validation_status"] = "skipped_blank"

        print("Blank note detected.")
        print("Gemini API call skipped.")

    else:

        try:

            # STEP 13: Pause between API calls

            if api_calls > 0:
                time.sleep(13)

            # STEP 14: Analyse note using Gemini

            api_calls += 1

            data, raw_response = analyse_note(
                str(note_text),
                return_raw=True
            )

            # Store original response exactly as returned

            result_row["raw_response"] = raw_response

            # STEP 15: Copy fields returned by Gemini

            if isinstance(data, dict):

                fields = [
                    "root_cause",
                    "confidence",
                    "summary",
                    "recommended_action"
                ]

                for field in fields:

                    if field in data:
                        result_row[field] = data[field]

                # STEP 16: Pydantic validation

                validated_data = FollowupInsight(**data)

                # STEP 17: Allowed root cause validation

                if validated_data.root_cause not in ALLOWED_ROOT_CAUSES:

                    raise ValueError(
                        "Root cause is not in the allowed list."
                    )

                result_row["validation_status"] = "valid"

                print("Validation successful.")

            else:

                result_row["validation_status"] = "invalid"

                print("Invalid response format.")

        except Exception as error:

            result_row["validation_status"] = "invalid"

            print("Validation or API error:", error)

    # STEP 18: Save every result in the list

    results.append(result_row)


# =====================================================
# STEP 19: CREATE OUTPUT CSV
# =====================================================

output_columns = [
    "note_id",
    "appointment_id",
    "root_cause",
    "confidence",
    "summary",
    "recommended_action",
    "validation_status",
    "raw_response"
]

output_df = pd.DataFrame(
    results,
    columns=output_columns
)


# STEP 20: SAVE CSV FILE

output_df.to_csv(
    "notes_analysed.csv",
    index=False
)


# =====================================================
# FINAL OUTPUT
# =====================================================

print("\n===================================")
print("TASK 4.2 COMPLETED SUCCESSFULLY")
print("===================================")

print("Total notes processed:", len(output_df))
print("Gemini API calls made:", api_calls)

print("\nValidation status counts:")
print(output_df["validation_status"].value_counts(dropna=False))

print("\nOutput CSV created: notes_analysed.csv")

print("\nFirst 10 results:")
print(output_df.to_string(index=False))

print("\n===================================")
print("TASK 4.2 COMPLETED SUCCESSFULLY")