"""
Conflict Analysis Service (rewritten)
Uses GeminiOCRService for:
 - extracting medicines from OCR text (or images if needed)
 - normalizing medicine names
 - performing conflict analysis (drug-drug + allergy)
This version removes any hardcoded medicine lists and relies solely on Gemini.
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional

from .gemini_service import GeminiOCRService

logger = logging.getLogger(__name__)


class ConflictAnalysisService:
    """Service for analyzing prescription conflicts and drug interactions using Gemini AI"""

    def __init__(self):
        self.gemini_service = GeminiOCRService()
        logger.info("ConflictAnalysisService initialized with GeminiOCRService")

    # --------------------------
    # Public API - Single prescription (text) analysis
    # --------------------------
    def analyze_conflicts(self, prescription_text: str, current_medications: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze conflicts for a single prescription text (OCR output) vs current medications/allergies.

        Args:
            prescription_text: Raw OCR text OR a JSON string containing {"medicines": [...]}
            current_medications: Optional list of user's known current medications or allergies (strings)

        Returns:
            Structured analysis result (dict)
        """
        try:
            logger.info("Starting single-prescription conflict analysis")

            # 1) Obtain medicines from the prescription text.
            # If the frontend already provided JSON with medicines (e.g., {"medicines": [...]})
            # try to parse it first. Otherwise, call Gemini to extract medicines from text.
            doctor_a_medicines = []
            try:
                # Attempt to parse as JSON with "medicines" key
                parsed = json.loads(prescription_text)
                if isinstance(parsed, dict) and "medicines" in parsed:
                    doctor_a_medicines = parsed.get("medicines", []) or []
                    logger.debug("Prescription text contained 'medicines' JSON; using it directly")
            except Exception:
                # Not JSON — proceed to ask Gemini to extract from text
                logger.debug("Prescription text is not JSON; extracting medicines via Gemini from text")
                doctor_a_medicines = self._extract_medicines_from_text_via_gemini(prescription_text)

            # Normalize medicines (safety)
            doctor_a_medicines = self._normalize_list(doctor_a_medicines)

            # Doctor B empty in this single-prescription flow
            doctor_b_medicines: List[str] = []

            # 2) Call Gemini conflict analysis
            gemini_result = self.gemini_service.analyze_medicine_conflicts(
                doctor_a_medicines=doctor_a_medicines,
                doctor_b_medicines=doctor_b_medicines,
                user_allergies=current_medications
            )

            # 3) If Gemini returned valid result, transform to our API shape
            if gemini_result:
                return self._transform_gemini_result_single(
                    gemini_result, doctor_a_medicines, current_medications
                )

            # 4) Fallback response if Gemini failed
            logger.warning("Gemini returned no result; returning safe fallback for single-prescription analysis")
            return {
                'prescription_medicines': doctor_a_medicines,
                'current_medications': current_medications or [],
                'drug_interactions': [],
                'allergy_conflicts': [],
                'total_conflicts': 0,
                'risk_level': 'UNKNOWN',
                'analysis_summary': 'Unable to analyze conflicts at this time. Please consult your healthcare provider.',
                'success': True
            }

        except Exception as e:
            logger.error(f"analyze_conflicts error: {e}")
            return {
                'error': str(e),
                'prescription_medicines': [],
                'current_medications': current_medications or [],
                'drug_interactions': [],
                'allergy_conflicts': [],
                'total_conflicts': 0,
                'risk_level': 'UNKNOWN',
                'success': False
            }

    # --------------------------
    # Public API - Multi-prescription analysis
    # --------------------------
    def analyze_multi_prescription_conflicts(self,
                                             doctor_a_medicines: List[str],
                                             doctor_b_medicines: List[str],
                                             user_allergies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze conflicts between two lists of medicines (Doctor A & Doctor B).

        Args:
            doctor_a_medicines: List[str]
            doctor_b_medicines: List[str]
            user_allergies: Optional[List[str]]

        Returns:
            Structured analysis result (dict)
        """
        try:
            logger.info("Starting multi-prescription conflict analysis")

            # Normalize both lists
            doctor_a_medicines = self._normalize_list(doctor_a_medicines)
            doctor_b_medicines = self._normalize_list(doctor_b_medicines)

            # Ask Gemini to analyze conflicts between the two lists
            gemini_result = self.gemini_service.analyze_medicine_conflicts(
                doctor_a_medicines=doctor_a_medicines,
                doctor_b_medicines=doctor_b_medicines,
                user_allergies=user_allergies
            )

            if gemini_result:
                return self._transform_gemini_result_multi(
                    gemini_result, doctor_a_medicines, doctor_b_medicines, user_allergies
                )

            logger.warning("Gemini returned no result for multi-prescription analysis; returning fallback")
            return {
                'doctor_a_medicines': doctor_a_medicines,
                'doctor_b_medicines': doctor_b_medicines,
                'prescription_medicines': doctor_a_medicines + doctor_b_medicines,
                'current_medications': user_allergies or [],
                'drug_interactions': [],
                'allergy_conflicts': [],
                'total_conflicts': 0,
                'risk_level': 'UNKNOWN',
                'analysis_summary': 'Unable to analyze conflicts at this time. Please consult your healthcare provider.',
                'success': True
            }

        except Exception as e:
            logger.error(f"analyze_multi_prescription_conflicts error: {e}")
            return {
                'error': str(e),
                'doctor_a_medicines': doctor_a_medicines,
                'doctor_b_medicines': doctor_b_medicines,
                'prescription_medicines': doctor_a_medicines + doctor_b_medicines,
                'current_medications': user_allergies or [],
                'drug_interactions': [],
                'allergy_conflicts': [],
                'total_conflicts': 0,
                'risk_level': 'UNKNOWN',
                'success': False
            }

    # --------------------------
    # Internal helpers
    # --------------------------
    def _extract_medicines_from_text_via_gemini(self, text: str) -> List[str]:
        """
        Ask Gemini to extract medicine names from a block of OCR text.
        Returns a normalized list of medicine names (lowercase).
        """
        try:
            if not text or not text.strip():
                return []

            prompt = f"""
You are a medical OCR specialist.

TASK:
1. From the following OCR text, extract ONLY medicine names (generic or brand).
2. Ignore dosages, strengths, symbols, non-medicine words.
3. Apply the ZERO-GUESSING rule: only include names you are at least 100% certain about.
4. Return a JSON block inside <json> tags exactly like:
<json>{{ "medicines": [] }}</json>

OCR_TEXT:
\"\"\"{text}\"\"\"
"""

            # Use the same model instance available in GeminiOCRService
            response = self.gemini_service.model.generate_content(prompt)

            if not response or not response.text:
                logger.warning("Gemini returned empty response for text extraction")
                return []

            # Extract JSON using gemini_service helper if available, otherwise use local regex
            try:
                json_text = self.gemini_service._extract_json(response.text)
            except Exception:
                # fallback extraction
                m = re.search(r"<json>([\s\S]*?)</json>", response.text)
                if not m:
                    logger.warning("No <json> block found in Gemini text extraction response")
                    return []
                json_text = m.group(1)

            data = json.loads(json_text)
            meds = data.get("medicines", []) or []

            # Normalize using the gemini normalization layer
            meds = self.gemini_service.normalize_medicines(meds)
            return meds

        except Exception as e:
            logger.error(f"_extract_medicines_from_text_via_gemini error: {e}")
            return []

    def _normalize_list(self, meds: Optional[List[str]]) -> List[str]:
        """Normalize and deduplicate a list of medicines using gemini_service.normalize_medicines"""
        try:
            if not meds:
                return []
            return self.gemini_service.normalize_medicines(meds)
        except Exception as e:
            logger.warning(f"Normalization failed: {e}")
            # Fallback minimal normalization
            cleaned = []
            for m in meds or []:
                if not m:
                    continue
                candidate = str(m).strip().lower()
                candidate = re.sub(r"[^a-z]", "", candidate)
                if candidate and candidate not in cleaned:
                    cleaned.append(candidate)
            return cleaned

    def _transform_gemini_result_single(self, gemini_result: Dict[str, Any], doctor_a_medicines: List[str], current_medications: Optional[List[str]]):
        """Transform Gemini JSON into the API response for single-prescription analysis"""
        try:
            drug_interactions = []
            allergy_conflicts = []

            for interaction in gemini_result.get('drug_interactions', []):
                # Expect interaction["pair"] like "drug1 + drug2"
                pair = interaction.get('pair', '')
                meds = [m.strip() for m in pair.split('+')] if pair else []
                # Ensure normalized meds
                meds = [m.lower() for m in meds if m]
                drug_interactions.append({
                    'type': 'drug_interaction',
                    'medicines': meds,
                    'reason': interaction.get('reason', ''),
                    'severity': interaction.get('severity', 'MEDIUM') if interaction.get('severity') else 'MEDIUM'
                })

            for conflict in gemini_result.get('allergy_conflicts', []):
                allergy_conflicts.append({
                    'type': 'allergy_conflict',
                    'medicine': (conflict.get('medicine') or '').lower(),
                    'allergy': (conflict.get('allergy') or '').lower(),
                    'reason': conflict.get('reason', ''),
                    'severity': conflict.get('severity', 'HIGH')
                })

            risk_level = gemini_result.get('risk_level', 'LOW')
            total_conflicts = len(drug_interactions) + len(allergy_conflicts)

            return {
                'prescription_medicines': doctor_a_medicines,
                'current_medications': current_medications or [],
                'drug_interactions': drug_interactions,
                'allergy_conflicts': allergy_conflicts,
                'total_conflicts': total_conflicts,
                'risk_level': risk_level,
                'analysis_summary': gemini_result.get('message') or self._generate_summary(drug_interactions, allergy_conflicts, risk_level),
                'success': True
            }

        except Exception as e:
            logger.error(f"_transform_gemini_result_single error: {e}")
            return {
                'prescription_medicines': doctor_a_medicines,
                'current_medications': current_medications or [],
                'drug_interactions': [],
                'allergy_conflicts': [],
                'total_conflicts': 0,
                'risk_level': 'UNKNOWN',
                'analysis_summary': 'Error processing Gemini result',
                'success': False
            }

    def _transform_gemini_result_multi(self, gemini_result: Dict[str, Any], doctor_a_medicines: List[str], doctor_b_medicines: List[str], user_allergies: Optional[List[str]]):
        """Transform Gemini JSON into API response for multi-prescription analysis"""
        try:
            drug_interactions = []
            allergy_conflicts = []

            for interaction in gemini_result.get('drug_interactions', []):
                pair = interaction.get('pair', '')
                meds = [m.strip() for m in pair.split('+')] if pair else []
                meds = [m.lower() for m in meds if m]
                drug_interactions.append({
                    'type': 'drug_interaction',
                    'medicines': meds,
                    'reason': interaction.get('reason', ''),
                    'severity': interaction.get('severity', 'MEDIUM')
                })

            for conflict in gemini_result.get('allergy_conflicts', []):
                allergy_conflicts.append({
                    'type': 'allergy_conflict',
                    'medicine': (conflict.get('medicine') or '').lower(),
                    'allergy': (conflict.get('allergy') or '').lower(),
                    'reason': conflict.get('reason', ''),
                    'severity': conflict.get('severity', 'HIGH')
                })

            risk_level = gemini_result.get('risk_level', 'LOW')
            total_conflicts = len(drug_interactions) + len(allergy_conflicts)

            return {
                'doctor_a_medicines': doctor_a_medicines,
                'doctor_b_medicines': doctor_b_medicines,
                'prescription_medicines': doctor_a_medicines + doctor_b_medicines,
                'current_medications': user_allergies or [],
                'drug_interactions': drug_interactions,
                'allergy_conflicts': allergy_conflicts,
                'total_conflicts': total_conflicts,
                'risk_level': risk_level,
                'analysis_summary': gemini_result.get('message') or self._generate_summary(drug_interactions, allergy_conflicts, risk_level),
                'success': True
            }

        except Exception as e:
            logger.error(f"_transform_gemini_result_multi error: {e}")
            return {
                'doctor_a_medicines': doctor_a_medicines,
                'doctor_b_medicines': doctor_b_medicines,
                'prescription_medicines': doctor_a_medicines + doctor_b_medicines,
                'current_medications': user_allergies or [],
                'drug_interactions': [],
                'allergy_conflicts': [],
                'total_conflicts': 0,
                'risk_level': 'UNKNOWN',
                'analysis_summary': 'Error processing Gemini result',
                'success': False
            }

    # --------------------------
    # Summary generation (human readable)
    # --------------------------
    def _generate_summary(self, drug_interactions: List[Dict], allergy_conflicts: List[Dict], risk_level: str) -> str:
        total_conflicts = len(drug_interactions) + len(allergy_conflicts)
        if total_conflicts == 0:
            return "No conflicts detected between prescriptions and allergies."

        summary_parts = []
        if allergy_conflicts:
            summary_parts.append(f"{len(allergy_conflicts)} allergy conflict(s) found")
        if drug_interactions:
            summary_parts.append(f"{len(drug_interactions)} drug interaction(s) detected")

        summary = f"{total_conflicts} total conflicts found: " + ", ".join(summary_parts)
        summary += f". Overall risk level: {risk_level}."
        if risk_level == 'HIGH':
            summary += " Immediate medical consultation recommended."
        elif risk_level == 'MEDIUM':
            summary += " Caution advised - consult healthcare provider."

        return summary
