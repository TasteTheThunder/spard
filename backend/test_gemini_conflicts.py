#!/usr/bin/env python3
"""
Test script for Gemini-based conflict analysis
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.gemini_service import GeminiOCRService
from services.conflict_service import ConflictAnalysisService

def test_gemini_conflict_analysis():
    """Test the Gemini conflict analysis functionality"""
    
    print("🧪 Testing Gemini Conflict Analysis")
    print("=" * 50)
    
    try:
        # Check if Gemini API key is available
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY environment variable not found!")
            print("Please set your Gemini API key in the .env file")
            return False
        
        print(f"✅ Gemini API key found: {api_key[:10]}...")
        
        # Initialize services
        gemini_service = GeminiOCRService()
        conflict_service = ConflictAnalysisService()
        
        print("✅ Services initialized successfully")
        
        # Test case 1: Basic drug interactions
        print("\n📋 Test Case 1: Basic Drug Interactions")
        print("-" * 40)
        
        doctor_a_medicines = ['metformin', 'ibuprofen']
        doctor_b_medicines = ['aspirin', 'warfarin']
        user_allergies = ['penicillin']
        
        print(f"Doctor A medicines: {doctor_a_medicines}")
        print(f"Doctor B medicines: {doctor_b_medicines}")
        print(f"User allergies: {user_allergies}")
        
        result = gemini_service.analyze_medicine_conflicts(
            doctor_a_medicines, 
            doctor_b_medicines, 
            user_allergies
        )
        
        if result:
            print("✅ Gemini analysis successful!")
            print(f"Interactions found: {len(result.get('interactions', []))}")
            print(f"Allergy conflicts: {len(result.get('allergy_conflicts', []))}")
            print(f"Risk level: {result.get('risk_level', 'Unknown')}")
            print(f"Message: {result.get('message', 'No message')}")
            
            # Show detailed results
            for interaction in result.get('interactions', []):
                print(f"  🔗 Interaction: {interaction}")
                
            for conflict in result.get('allergy_conflicts', []):
                print(f"  ⚠️  Allergy conflict: {conflict}")
        else:
            print("❌ Gemini analysis failed")
            return False
        
        # Test case 2: Single prescription analysis
        print("\n📋 Test Case 2: Single Prescription Analysis")
        print("-" * 40)
        
        prescription_text = "Doctor A Medications: metformin, lisinopril\nPatient has penicillin allergy"
        current_medications = ['penicillin']
        
        analysis_result = conflict_service.analyze_conflicts(
            prescription_text,
            current_medications
        )
        
        if analysis_result.get('success'):
            print("✅ Single prescription analysis successful!")
            print(f"Medicines found: {analysis_result.get('prescription_medicines', [])}")
            print(f"Total conflicts: {analysis_result.get('total_conflicts', 0)}")
            print(f"Risk level: {analysis_result.get('risk_level', 'Unknown')}")
            print(f"Summary: {analysis_result.get('analysis_summary', 'No summary')}")
        else:
            print("❌ Single prescription analysis failed")
            print(f"Error: {analysis_result.get('error', 'Unknown error')}")
        
        # Test case 3: Multi-prescription analysis
        print("\n📋 Test Case 3: Multi-Prescription Analysis")
        print("-" * 40)
        
        multi_result = conflict_service.analyze_multi_prescription_conflicts(
            doctor_a_medicines=['amoxicillin', 'ibuprofen'],
            doctor_b_medicines=['aspirin', 'warfarin'],
            user_allergies=['penicillin']
        )
        
        if multi_result.get('success'):
            print("✅ Multi-prescription analysis successful!")
            print(f"Doctor A medicines: {multi_result.get('doctor_a_medicines', [])}")
            print(f"Doctor B medicines: {multi_result.get('doctor_b_medicines', [])}")
            print(f"Total conflicts: {multi_result.get('total_conflicts', 0)}")
            print(f"Risk level: {multi_result.get('risk_level', 'Unknown')}")
        else:
            print("❌ Multi-prescription analysis failed")
            print(f"Error: {multi_result.get('error', 'Unknown error')}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.exception("Test error details:")
        return False

if __name__ == "__main__":
    success = test_gemini_conflict_analysis()
    sys.exit(0 if success else 1)