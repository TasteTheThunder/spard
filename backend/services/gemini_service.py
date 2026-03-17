"""
Gemini AI Vision API service for OCR + Medicine Extraction + Conflict Analysis
"""
import google.generativeai as genai
import base64
from PIL import Image
import io
import logging
import json
import re
from config import Config

# Configure logging
logger = logging.getLogger(__name__)

class GeminiOCRService:
    """Service for handling Gemini Vision API OCR, medicine extraction and conflict analysis"""

    def __init__(self):
        """Initialize Gemini service with API key"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini OCR service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise

    # -------------------------------------------------------------
    # NORMALIZATION LAYER (NEW)
    # -------------------------------------------------------------
    def normalize_medicines(self, medicines):
        """Normalize medicine names extracted from Gemini"""
        normalized = []
        corrections = {
            "amoxcillin": "amoxicillin",
            "amoxillin": "amoxicillin",
            "amoxil": "amoxicillin",
            "pantaprazole": "pantoprazole",
            "pantaprozole": "pantoprazole",
            "paracetmol": "paracetamol",
            "paracetemol": "paracetamol",
            "doxycyclin": "doxycycline",
            "cetrezine": "cetirizine",
            "cetrizine": "cetirizine",
            "metfornin": "metformin",
        }

        for med in medicines:
            med = med.strip().lower()

            # Remove trailing punctuation / numbers
            med = re.sub(r"[^a-z]", "", med)

            # Apply known corrections
            if med in corrections:
                med = corrections[med]

            if med and med not in normalized:
                normalized.append(med)

        return normalized

    # -------------------------------------------------------------
    # 1️⃣ COMBINED OCR + MEDICINE EXTRACTION
    # -------------------------------------------------------------
    def extract_medicines_from_image(self, image_data, doctor):
        try:
            if isinstance(image_data, bytes):
                image_bytes = image_data
            else:
                image_bytes = base64.b64decode(image_data)

            image = Image.open(io.BytesIO(image_bytes))

            prompt = """
You are a medical OCR specialist.

TASK:
1. Read the prescription image.
2. Extract ONLY real medicine names (generic or brand).
3. Ignore dosage, strengths, symbols, timings.
4. Output ONLY JSON wrapped inside <json> tags:

<json>
{
  "medicines": []
}
</json>

ZERO-GUESSING:
- Include a name ONLY if 100% sure it is a medicine.
- Never hallucinate.
- Never add explanations.
"""

            response = self.model.generate_content([prompt, image])
            text = response.text

            json_text = self._extract_json(text)
            data = json.loads(json_text)

            medicines = data.get("medicines", [])

            # APPLY NORMALIZATION HERE (VERY IMPORTANT)
            medicines = self.normalize_medicines(medicines)

            return medicines

        except Exception as e:
            logger.error(f"Gemini OCR Error: {e}")
            return []

    # Extract JSON from <json> block
    def _extract_json(self, gemini_text):
        match = re.search(r"<json>([\s\S]*?)</json>", gemini_text)
        if not match:
            raise ValueError("JSON block not found in Gemini output")
        return match.group(1)

    # -------------------------------------------------------------
    # 2️⃣ DRUG CONFLICT ANALYSIS USING GEMINI
    # -------------------------------------------------------------
    def analyze_medicine_conflicts(self, doctor_a_medicines, doctor_b_medicines, user_allergies=None):
        try:
            prompt = self._create_conflict_analysis_prompt(
                doctor_a_medicines,
                doctor_b_medicines,
                user_allergies
            )

            response = self.model.generate_content(prompt)

            if not response or not response.text:
                return None

            logger.info(f"Gemini raw response: {response.text}")

            try:
                json_text = self._extract_json(response.text)
                result = json.loads(json_text)
                return result

            except Exception as e:
                logger.warning(f"JSON parsing failed: {e}")
                return self._create_fallback_response(
                    doctor_a_medicines,
                    doctor_b_medicines,
                    response.text
                )

        except Exception as e:
            logger.error(f"Gemini conflict analysis error: {e}")
            return None

    # -------------------------------------------------------------
    # Fallback if JSON is bad
    # -------------------------------------------------------------
    def _create_fallback_response(self, doctor_a, doctor_b, raw):
        return {
            "doctorA_medicines": doctor_a,
            "doctorB_medicines": doctor_b,
            "interactions": [],
            "allergy_conflicts": [],
            "risk_level": "LOW",
            "message": "Fallback: Could not parse Gemini JSON. Review raw output."
        }

    # -------------------------------------------------------------
    # 3️⃣ SAFE ZERO-HALLUCINATION CONFLICT PROMPT
    # -------------------------------------------------------------
    def _create_conflict_analysis_prompt(self, doctor_a_medicines, doctor_b_medicines, user_allergies):

        doctor_a_json = json.dumps(doctor_a_medicines)
        doctor_b_json = json.dumps(doctor_b_medicines)
        allergy_json = json.dumps(user_allergies) if user_allergies else "[]"

        return f"""
You are a certified clinical pharmacology AI.  
You MUST analyze **both**:
1. Verified drug–drug interactions  
2. Verified drug–allergy conflicts  

You MUST ALWAYS evaluate **both categories independently**.

Your output MUST BE ONLY valid JSON inside <json> tags with ZERO text outside.

EXPECTED SCHEMA (follow EXACTLY):

<json>
{{
  "doctorA_medicines": [],
  "doctorB_medicines": [],
  "drug_interactions": [
    {{
      "medicines": ["drug1", "drug2"],
      "reason": "Clear clinical explanation of the drug–drug interaction mechanism.",
      "severity": "HIGH|MEDIUM|LOW"
    }}
  ],
  "allergy_conflicts": [
    {{
      "medicine": "medicine_name",
      "allergy": "allergy_name",
      "reason": "Clinical explanation of the allergic conflict.",
      "severity": "HIGH|MEDIUM|LOW"
    }}
  ],
  "risk_level": "HIGH|MEDIUM|LOW",
  "analysis_summary": "One short medical summary covering BOTH drug interactions and allergy conflicts."
}}
</json>

STRICT RULES:
- You MUST evaluate drug–drug interactions even if allergy conflicts exist.
- You MUST evaluate allergy conflicts even if drug interactions exist.
- NEVER hallucinate medicine names.
- Use ONLY the medicines EXACTLY as provided.
- Use FDA / WHO / NICE verified medical information.
- If a category has no results, return an **empty list** (not null, not omitted).
- NEVER output anything outside <json>…</json>.

INPUT:
Doctor A medicines = {doctor_a_json}
Doctor B medicines = {doctor_b_json}
User allergies = {allergy_json}

Return ONLY the JSON.
"""





    # -------------------------------------------------------------
    # 4️⃣ HEALTH CHECK
    # -------------------------------------------------------------
    def validate_service(self):
        try:
            self.model.generate_content("ping")
            return True
        except Exception as e:
            logger.error(f"Gemini service validation failed: {e}")
            return False
