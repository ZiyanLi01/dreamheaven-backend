#!/usr/bin/env python3
"""
Test script to verify frontend integration with the updated API
"""

import requests
import json

def test_frontend_integration():
    """Test the frontend integration scenarios"""
    print("🧪 Testing Frontend Integration")
    print("=" * 40)
    
    base_url = "http://localhost:8000/api/listings"
    
    # Test cases based on frontend requests
    test_cases = [
        {
            "name": "Frontend request: location + sort",
            "params": {
                "location": "Los Angeles, CA",
                "sortBy": "price",
                "sortOrder": "asc"
            },
            "expected": "Should return LA properties sorted by price ascending"
        },
        {
            "name": "Frontend request: bed 2+ + bath Any + rent For Rent",
            "params": {
                "bed": "2+",
                "bath": "Any",
                "rent": "For Rent",
                "sortBy": "price",
                "sortOrder": "desc"
            },
            "expected": "Should return 2+ bed properties for rent, sorted by price descending"
        },
        {
            "name": "Frontend request: specific bed/bath + For Sale",
            "params": {
                "bed": "3",
                "bath": "2",
                "rent": "For Sale",
                "sortBy": "bedrooms",
                "sortOrder": "asc"
            },
            "expected": "Should return 3BR/2BA properties for sale, sorted by bedrooms"
        },
        {
            "name": "Frontend request: Any filters (no filtering)",
            "params": {
                "bed": "Any",
                "bath": "Any",
                "sortBy": "square_feet",
                "sortOrder": "desc"
            },
            "expected": "Should return all properties sorted by square footage"
        },
        {
            "name": "Frontend request: location + bed 2+",
            "params": {
                "location": "New York, NY",
                "bed": "2+",
                "sortBy": "price",
                "sortOrder": "asc"
            },
            "expected": "Should return NY properties with 2+ bedrooms, sorted by price"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            response = requests.get(base_url, params=test_case['params'])
            
            if response.status_code == 200:
                data = response.json()
                results_count = len(data.get('results', []))
                total_count = data.get('total', 0)
                
                print(f"   ✅ Status: 200")
                print(f"   📊 Results: {results_count} (Total: {total_count})")
                
                if results_count > 0:
                    # Show first result details
                    first_result = data['results'][0]
                    print(f"   🏠 Sample: {first_result.get('address', 'N/A')}")
                    print(f"      🛏️  {first_result.get('bedrooms', 0)}BR, 🚿 {first_result.get('bathrooms', 0)}BA")
                    print(f"      📍 {first_result.get('location', 'N/A')}")
                    print(f"      💰 ${first_result.get('price', 0):,.0f}")
                    print(f"      🏷️  {first_result.get('status', 'N/A')}")
                    print(f"      🏠 {first_result.get('sqft', 0)} sqft")
                    
                    # Verify required fields are present
                    required_fields = ['id', 'address', 'location', 'bedrooms', 'bathrooms', 'price', 'sqft', 'imageUrl']
                    missing_fields = [field for field in required_fields if field not in first_result or first_result[field] is None]
                    if missing_fields:
                        print(f"      ⚠️  Missing fields: {missing_fields}")
                    else:
                        print(f"      ✅ All required fields present")
                else:
                    print(f"   ⚠️  No results found")
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Test error handling
    print(f"\n🔍 Testing Error Handling:")
    
    # Test with invalid location format
    try:
        response = requests.get(base_url, params={"location": "InvalidLocation"})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Invalid location handled gracefully: {len(data.get('results', []))} results")
        else:
            print(f"   ❌ Invalid location caused error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error with invalid location: {str(e)}")
    
    # Test with invalid bed/bath values
    try:
        response = requests.get(base_url, params={"bed": "invalid", "bath": "invalid"})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Invalid bed/bath handled gracefully: {len(data.get('results', []))} results")
        else:
            print(f"   ❌ Invalid bed/bath caused error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error with invalid bed/bath: {str(e)}")
    
    print(f"\n🎉 Frontend integration testing completed!")

if __name__ == "__main__":
    test_frontend_integration() 