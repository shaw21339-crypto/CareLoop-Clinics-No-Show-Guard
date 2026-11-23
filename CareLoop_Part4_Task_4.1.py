# Part 4 — GenAI: turn call-centre notes into structured reasons, then recommend (22 marks)

# The model says who is at risk; the notes say why patients actually missed. You will use the Gemini API to
# read the  first 10 notes, force the answers into a fixed format, validate them with Pydantic, test the
# weak spots, and then combine everything into a recommendation.
# Allowed root_cause values: forgot_or_no_reminder, distance_or_transport, cost_or_fee, illness_or_emergency,
# work_or_schedule, other.

# Task 4.1 — One validated call (5 marks)
# Get a free key in Google AI Studio and install the library in Colab. Write a function
# analyse_note(note_text) that sends one note to the Gemini Flash model used in class, with a system
# instruction, a prompt built with the CRAFT parts (Context, Role, Action, Tone, Format), temperature=0,
# response_mime_type set to JSON, and a JSON response schema with four fields: root_cause
# (a plain string — do not make it an enum; the allowed values go in your prompt and are enforced afterwards
# by the check in Task 4.2), confidence (0–1), summary (at most 25 words), recommended_action. Set the
# thinking level to minimal as shown in Session 22.1, and give max_output_tokens plenty of room
# (1000 or more): on some models hidden reasoning tokens count against the limit and can cut the JSON off,
# which makes json.loads fail. Run it on note N001 and print the parsed dictionary. Shape of the call
# (follow your Session 22.1 notebook if any detail differs; the key is typed at run time):

# Solution

# ==========================================
# CARELOOP CLINICS
# PART 4 - TASK 4.1
# GenAI: turn call-centre notes into structured reasons, then recommend
# ==========================================

import os
import json
import pandas as pd

from dotenv import load_dotenv
from google import genai
from google.genai import types


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


# STEP 5: Define system instruction
SYSTEM_TEXT = """
You are a healthcare administration data analyst
working for CareLoop Clinics.

Analyse patient appointment follow-up notes.
Return accurate, professional and neutral results.
Follow the requested JSON response format exactly.
Do not invent information that is not present in the note.
"""


# STEP 6: Define CRAFT prompt
def build_prompt(note_text):

    prompt = f"""
    Context:
    CareLoop Clinics wants to understand why patients
    miss their scheduled appointments.

    Role:
    You are an experienced healthcare administration
    data analyst.

    Action:
    Analyse the following patient follow-up note.
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


# STEP 7: Define analysis function
def analyse_note(note_text):

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

    # Convert JSON response into Python dictionary
    result = json.loads(response.text)

    # Validate required fields
    required_fields = {
        "root_cause",
        "confidence",
        "summary",
        "recommended_action"
    }

    if set(result.keys()) != required_fields:
        raise ValueError("Incorrect JSON fields returned.")

    if not isinstance(result["root_cause"], str):
        raise ValueError("root_cause must be a string.")

    if not 0 <= result["confidence"] <= 1:
        raise ValueError("Confidence must be between 0 and 1.")

    if len(result["summary"].split()) > 25:
        raise ValueError("Summary exceeds 25 words.")

    return result


# STEP 8: Read follow-up notes
notes = pd.read_csv("followup_notes.csv")


# STEP 9: Find note N001
note_row = notes[
    notes["note_id"].astype(str).str.strip() == "N001"
]

if note_row.empty:
    raise ValueError("Note N001 was not found.")

note_text = str(note_row.iloc[0]["note_text"])


# STEP 10: Analyse note N001
result = analyse_note(note_text)


# STEP 11: Display output
print("TASK 4.1 - GEMINI NOTE ANALYSIS")
print("--------------------------------")

print("NOTE ID: N001")
print("ANALYSIS RESULT:")
print(result)

print("RESULT TYPE:", type(result))

print("\n===================================")
print("TASK 4.1 COMPLETED SUCCESSFULLY")
