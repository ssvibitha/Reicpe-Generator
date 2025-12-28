from google import genai
from google.genai.errors import ClientError
import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel, Field
import enum
from datetime import datetime
from config import Config

# ================= CONFIG =================
config = Config('.config')
API_KEY = config.api_key
MODEL_NAME = "gemini-3-flash-preview"
OUTPUT_FILE = "medical_report.json"

client = genai.Client(api_key=API_KEY)

# ================= UNIVERSAL SCHEMA MODEL =================
class UniversalHealthReport(BaseModel):
    source_metadata: dict = Field(default_factory=dict)
    patient_profile: dict = Field(default_factory=dict)
    encounter_info: dict = Field(default_factory=dict)
    symptoms: list = Field(default_factory=list)
    diagnoses: dict = Field(default_factory=dict)
    allergies: dict = Field(default_factory=dict)
    medications_current: list = Field(default_factory=list)
    lab_results: list = Field(default_factory=list)
    findings: dict = Field(default_factory=dict)
    lifestyle_and_risk: dict = Field(default_factory=dict)
    recommendations: dict = Field(default_factory=dict)
    system_generated: dict = Field(default_factory=dict)
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())


# ================= PROMPT =================
UNIVERSAL_PROMPT = """
You are a medical data extractor. Convert any medical document (clinical note, prescription, lab report, scan, handwritten text OCR) into STRICT JSON.

❗IMPORTANT RULES:
- JSON ONLY. No explanations or text outside JSON.
- If unknown or missing → null or [].
- Do NOT invent data. Only extract what is explicitly stated or strongly implied.
- Convert dates to ISO-8601 if possible, otherwise null.
- Gender must be exactly: "Male" | "Female" | "Other" | null
- report_type must be ONE of: lab | prescription | discharge | clinical_note | imaging | mixed | unknown

Return JSON in this EXACT structure:

{
  "source_metadata": {
    "input_type": "text | image | pdf | ocr | scan | unknown",
    "file_name": null,
    "capture_date": null
  },
  "patient_profile": {
    "name": null,
    "age": null,
    "gender": null,
    "patient_id": null
  },
  "encounter_info": {
    "report_date": null,
    "facility_name": null,
    "doctor_name": null,
    "department": null,
    "report_type": "unknown"
  },
  "symptoms": [],
  "diagnoses": {
    "primary": [],
    "secondary": []
  },
  "allergies": {
    "medications": [],
    "food": [],
    "environmental": [],
    "unknown_reported": false
  },
  "medications_current": [],
  "lab_results": [],
  "findings": {
    "physical_exam": [],
    "imaging_summary": [],
    "doctor_notes": []
  },
  "lifestyle_and_risk": {
    "habits": [],
    "dietary_notes": [],
    "risk_factors": []
  },
  "recommendations": {
    "follow_up": null,
    "next_appointment": null,
    "suggested_labs": [],
    "referrals": []
  },
  "system_generated": {
    "confidence_score": null,
    "processing_notes": null
  },
  "last_updated": null
}

Now EXTRACT JSON only:
"""


# ================= GEMINI CALL =================
def call_gemini(prompt: str, content: str):
    try:
        return client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, content],
            config={"temperature": 0.1}
        )
    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            return {"error": "❌ API QUOTA EXCEEDED — enable billing or retry later"}
        raise e


# ================= PARSER =================
def parse_document(file_path: str) -> dict:
    # detect input type by extension
    ext = file_path.split(".")[-1].lower()
    input_type = "text"
    if ext in ["jpg", "jpeg", "png"]:
        input_type = "image"
    elif ext in ["pdf"]:
        input_type = "pdf"

    # read file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return {"error": f"❌ Cannot read file: {file_path}"}

    # call AI
    response = call_gemini(UNIVERSAL_PROMPT, content)
    if response is None:
        return {"error": "❌ No response from API"}

    raw = response.text.strip()

    # validate
    try:
        report = UniversalHealthReport.model_validate_json(raw).model_dump()
    except Exception as e:
        # Fallback: try raw load to give debug output
        try:
            report = json.loads(raw)
        except:
            return {"error": "❌ Model returned invalid JSON", "raw_output": raw}

    # inject metadata
    report["source_metadata"]["input_type"] = input_type
    report["source_metadata"]["file_name"] = os.path.basename(file_path)
    report["last_updated"] = datetime.now().isoformat()

    return report


# ================= SAVE JSON =================
def save_json(data: dict):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ JSON saved to {OUTPUT_FILE}")


# ================= MAIN =================
if __name__ == "__main__":
    target_file = "target_file.txt"

    if not os.path.exists(target_file):
        print("❌ Input file not found")
        exit()

    result = parse_document(target_file)
    save_json(result)
