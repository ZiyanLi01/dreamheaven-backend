#!/usr/bin/env python3
"""
Test script to verify the new POST /api/search endpoint
"""

import requests
import json

def test_search_endpoint():
    """Test the POST search endpoint with various scenarios"""
    base_url = "http://localhost:8080/search"
    
    print("🔍 Testing POST /api/search Endpoint")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Basic location + sort",
            "payload": {
                "location": "Los Angeles, CA",
                "sortBy": "price",
                "sortOrder": "asc",
                "limit": 3
            },
            "expected": "Should return LA properties sorted by price ascending"
        },
        {
            "name": "Bed 2+ + Bath Any + For Rent",
            "payload": {
                "bed": "2+",
                "bath": "Any",
                "rent": "For Rent",
                "sortBy": "price",
                "sortOrder": "desc",
                "limit": 3
            },
            "expected": "Should return 2+ bed properties for rent, sorted by price descending"
        },
        {
            "name": "Specific bed/bath + For Sale",
            "payload": {
                "bed": "3",
                "bath": "2",
                "rent": "For Sale",
                "sortBy": "bedrooms",
                "sortOrder": "asc",
                "limit": 3
            },
            "expected": "Should return 3BR/2BA properties for sale, sorted by bedrooms"
        },
        {
            "name": "Any filters (no filtering)",
            "payload": {
                "bed": "Any",
                "bath": "Any",
                "sortBy": "square_feet",
                "sortOrder": "desc",
                "limit": 3
            },
            "expected": "Should return all properties sorted by square footage"
        },
        {
            "name": "Location + Bed 2+",
            "payload": {
                "location": "New York, NY",
                "bed": "2+",
                "sortBy": "price",
                "sortOrder": "asc",
                "limit": 3
            },
            "expected": "Should return NY properties with 2+ bedrooms, sorted by price"
        },
        {
            "name": "Empty payload (defaults)",
            "payload": {},
            "expected": "Should return default results with pagination"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            response = requests.post(
                base_url,
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                results_count = len(data.get('results', []))
                total_count = data.get('total', 0)
                
                print(f"   ✅ Status: 200")
                print(f"   📊 Results: {results_count} (Total: {total_count})")
                
                if results_count > 0:
                    # Show first result details
                    first_result = data['results'][0]
                    print(f"   🏠 Sample: {first_result.get('title', 'N/A')}")
                    print(f"      🛏️  {first_result.get('bedrooms', 0)}BR, 🚿 {first_result.get('bathrooms', 0)}BA")
                    print(f"      📍 {first_result.get('city', 'N/A')}, {first_result.get('state', 'N/A')}")
                    print(f"      💰 ${first_result.get('price_per_night', 0):,.0f}")
                    print(f"      🏷️  {first_result.get('property_type', 'N/A')}")
                    
                    # Verify required fields are present
                    required_fields = ['id', 'title', 'description', 'bedrooms', 'bathrooms', 'price_per_night', 'city', 'state', 'images']
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
    
    # Test with invalid JSON
    try:
        response = requests.post(
            base_url,
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        print(f"   {'✅' if response.status_code == 422 else '❌'} Invalid JSON handled: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error with invalid JSON: {str(e)}")
    
    # Test with invalid bed/bath values
    try:
        response = requests.post(
            base_url,
            json={"bed": "invalid", "bath": "invalid"},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Invalid bed/bath handled gracefully: {len(data.get('results', []))} results")
        else:
            print(f"   ❌ Invalid bed/bath caused error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error with invalid bed/bath: {str(e)}")
    
    print(f"\n🎉 POST search endpoint testing completed!")

if __name__ == "__main__":
    test_search_endpoint() 