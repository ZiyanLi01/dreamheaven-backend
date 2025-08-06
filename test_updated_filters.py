#!/usr/bin/env python3
"""
Test script to verify the updated filter logic
"""

import requests
import json

def test_updated_filters():
    """Test the updated filter logic"""
    print("🧪 Testing Updated Filter Logic")
    print("=" * 40)
    
    base_url = "http://localhost:8000/api/listings"
    
    # Test cases
    test_cases = [
        {
            "name": "Location filter (city, state)",
            "params": {"location": "Los Angeles, CA", "limit": 5},
            "expected": "Should return LA properties"
        },
        {
            "name": "Bedrooms 2+ filter",
            "params": {"bed": "2+", "limit": 5},
            "expected": "Should return properties with 2+ bedrooms"
        },
        {
            "name": "Bathrooms 2+ filter",
            "params": {"bath": "2+", "limit": 5},
            "expected": "Should return properties with 2+ bathrooms"
        },
        {
            "name": "Specific bedrooms filter",
            "params": {"bed": "3", "limit": 5},
            "expected": "Should return properties with exactly 3 bedrooms"
        },
        {
            "name": "For Rent filter",
            "params": {"rent": "For Rent", "limit": 5},
            "expected": "Should return properties with monthly rent prices"
        },
        {
            "name": "For Sale filter",
            "params": {"rent": "For Sale", "limit": 5},
            "expected": "Should return properties with sale prices"
        },
        {
            "name": "Combined filters",
            "params": {"location": "Los Angeles, CA", "bed": "2+", "bath": "2+", "rent": "For Rent", "limit": 5},
            "expected": "Should return LA properties with 2+ bed/bath for rent"
        },
        {
            "name": "Any filter (should not filter)",
            "params": {"bed": "Any", "bath": "Any", "limit": 5},
            "expected": "Should return all properties (no filtering)"
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
                else:
                    print(f"   ⚠️  No results found")
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🎉 Filter testing completed!")

if __name__ == "__main__":
    test_updated_filters() 