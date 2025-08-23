#!/usr/bin/env python3
"""
Simple test script to verify backend connection
Run this to confirm the backend is working correctly
"""

import requests
import json

def test_backend_connection():
    """Test the backend connection and endpoints"""
    base_url = "http://localhost:8080"
    
    print("🔍 Testing Backend Connection")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Health check: ERROR - {str(e)}")
    
    # Test 2: Debug endpoint
    try:
        response = requests.get(f"{base_url}/debug")
        if response.status_code == 200:
            data = response.json()
            print("✅ Debug endpoint: PASSED")
            print(f"   Supabase status: {data.get('supabase_status', 'unknown')}")
        else:
            print(f"❌ Debug endpoint: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Debug endpoint: ERROR - {str(e)}")
    
    # Test 3: Basic listings endpoint
    try:
        response = requests.get(f"{base_url}/listings/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Basic listings: PASSED")
            print(f"   Results: {len(data.get('results', {}))}")
            print(f"   Total: {data.get('total', 0)}")
        else:
            print(f"❌ Basic listings: FAILED (Status: {response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Basic listings: ERROR - {str(e)}")
    
    # Test 4: Frontend-style request
    try:
        params = {
            "location": "Los Angeles, CA",
            "sortBy": "price",
            "sortOrder": "asc"
        }
        response = requests.get(f"{base_url}/listings/", params=params)
        if response.status_code == 200:
            data = response.json()
            print("✅ Frontend request: PASSED")
            print(f"   Results: {len(data.get('results', {}))}")
            print(f"   Total: {data.get('total', 0)}")
        else:
            print(f"❌ Frontend request: FAILED (Status: {response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Frontend request: ERROR - {str(e)}")
    
    # Test 5: Complex filtering
    try:
        params = {
            "bed": "2+",
            "bath": "Any",
            "rent": "For Rent",
            "sortBy": "price",
            "sortOrder": "desc"
        }
        response = requests.get(f"{base_url}/listings/", params=params)
        if response.status_code == 200:
            data = response.json()
            print("✅ Complex filtering: PASSED")
            print(f"   Results: {len(data.get('results', {}))}")
            print(f"   Total: {data.get('total', 0)}")
        else:
            print(f"❌ Complex filtering: FAILED (Status: {response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Complex filtering: ERROR - {str(e)}")
    
    print("\n🎯 Backend Test Summary:")
    print("If all tests passed, your backend is working correctly!")
    print("If any failed, check the error messages above.")

if __name__ == "__main__":
    test_backend_connection() 