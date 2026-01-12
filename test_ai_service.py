"""
Test script for AI Service
Verifies that the AI service is properly configured and working
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ai_service import get_ai_service


def test_ai_service():
    """Test the AI service initialization and basic functionality"""
    
    print("=" * 60)
    print("AI Service Test")
    print("=" * 60)
    
    # Test 1: Initialize service
    print("\n[Test 1] Initializing AI Service...")
    try:
        ai_service = get_ai_service()
        print("✓ AI Service initialized successfully")
        print(f"  Model: {ai_service.current_model}")
        print(f"  Available: {ai_service.is_available()}")
    except Exception as e:
        print(f"✗ Failed to initialize: {str(e)}")
        return
    
    # Test 2: Check configuration
    print("\n[Test 2] Checking Configuration...")
    try:
        model_info = ai_service.get_model_info()
        print("✓ Configuration loaded:")
        for key, value in model_info.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"✗ Failed to load configuration: {str(e)}")
    
    # Test 3: Test connection
    print("\n[Test 3] Testing API Connection...")
    try:
        result = ai_service.test_connection()
        if result['success']:
            print("✓ Connection test passed")
            print(f"  Response: {result['response']}")
        else:
            print(f"✗ Connection test failed: {result['message']}")
    except Exception as e:
        print(f"✗ Connection test error: {str(e)}")
    
    # Test 4: Code completion
    print("\n[Test 4] Testing Code Completion...")
    try:
        code_before = """def calculate_sum(a, b):
    \"\"\"Calculate sum of two numbers\"\"\"
    """
        code_after = ""
        current_line = "    "
        
        completion = ai_service.generate_completion_sync(
            code_before=code_before,
            code_after=code_after,
            current_line=current_line,
            file_name="test.py",
            language="python"
        )
        
        if completion:
            print("✓ Code completion generated:")
            print(f"  {repr(completion[:100])}...")
        else:
            print("✗ No completion generated")
    except Exception as e:
        print(f"✗ Code completion error: {str(e)}")
    
    # Test 5: Code explanation
    print("\n[Test 5] Testing Code Explanation...")
    try:
        code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
        
        explanation = ai_service.explain_code(
            code=code,
            file_name="test.py",
            language="python"
        )
        
        if explanation and "AI service is not available" not in explanation:
            print("✓ Code explanation generated:")
            print(f"  {explanation[:150]}...")
        else:
            print("✗ No explanation generated")
    except Exception as e:
        print(f"✗ Code explanation error: {str(e)}")
    
    # Test 6: Error correction
    print("\n[Test 6] Testing Error Correction...")
    try:
        buggy_code = """def divide(a, b):
    return a / b

result = divide(10, 0)"""
        
        correction = ai_service.correct_error(
            code=buggy_code,
            error_message="ZeroDivisionError: division by zero",
            file_name="test.py",
            language="python"
        )
        
        if correction['corrected_code']:
            print("✓ Error correction generated:")
            print(f"  Analysis: {correction['analysis'][:100]}...")
        else:
            print("✗ No correction generated")
    except Exception as e:
        print(f"✗ Error correction error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_ai_service()
