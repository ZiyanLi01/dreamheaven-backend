#!/usr/bin/env python3
"""
Test script to verify the new response format with UUID keys
"""

import requests
import json

def test_new_response_format():
    """Test the new response format with UUID keys"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing New Response Format (UUID Keys)")
    print("=" * 50)
    
    # Test 1: Listings endpoint
    print("\n1. Testing /api/listings endpoint:")
    try:
        response = requests.get(f"{base_url}/api/listings/?limit=3")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            
            print(f"   ✅ Status: 200")
            print(f"   📊 Results type: {type(results).__name__}")
            print(f"   📊 Results count: {len(results)}")
            print(f"   📊 Total: {data.get('total', 0)}")
            
            if results:
                # Show sample keys and values
                sample_key = list(results.keys())[0]
                sample_value = results[sample_key]
                print(f"   🔑 Sample key: {sample_key}")
                print(f"   🏠 Sample listing: {sample_value.get('address', 'N/A')}")
                print(f"      💰 ${sample_value.get('price', 0):,.0f}")
                print(f"      🛏️  {sample_value.get('bedrooms', 0)}BR, 🚿 {sample_value.get('bathrooms', 0)}BA")
                
                # Verify structure
                required_fields = ['id', 'address', 'location', 'bedrooms', 'bathrooms', 'price', 'imageUrl']
                missing_fields = [field for field in required_fields if field not in sample_value]
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
    
    # Test 2: Search endpoint (POST)
    print("\n2. Testing /api/search endpoint (POST):")
    try:
        response = requests.post(
            f"{base_url}/api/search/",
            json={"limit": 3},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            
            print(f"   ✅ Status: 200")
            print(f"   📊 Results type: {type(results).__name__}")
            print(f"   📊 Results count: {len(results)}")
            print(f"   📊 Total: {data.get('total', 0)}")
            
            if results:
                # Show sample keys and values
                sample_key = list(results.keys())[0]
                sample_value = results[sample_key]
                print(f"   🔑 Sample key: {sample_key}")
                print(f"   🏠 Sample listing: {sample_value.get('title', 'N/A')}")
                print(f"      💰 ${sample_value.get('price_per_night', 0):,.0f}")
                print(f"      🛏️  {sample_value.get('bedrooms', 0)}BR, 🚿 {sample_value.get('bathrooms', 0)}BA")
                
                # Verify structure
                required_fields = ['id', 'title', 'description', 'bedrooms', 'bathrooms', 'price_per_night', 'city', 'state']
                missing_fields = [field for field in required_fields if field not in sample_value]
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
    
    # Test 3: Filtered search
    print("\n3. Testing filtered search:")
    try:
        response = requests.post(
            f"{base_url}/api/search/",
            json={
                "location": "Los Angeles, CA",
                "bed": "2+",
                "limit": 2
            },
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            
            print(f"   ✅ Status: 200")
            print(f"   📊 Results count: {len(results)}")
            print(f"   📊 Total: {data.get('total', 0)}")
            
            if results:
                # Verify all results have 2+ bedrooms
                all_valid = all(
                    results[key].get('bedrooms', 0) >= 2 
                    for key in results.keys()
                )
                print(f"   ✅ All results have 2+ bedrooms: {all_valid}")
                
                # Show sample
                sample_key = list(results.keys())[0]
                sample_value = results[sample_key]
                print(f"   🏠 Sample: {sample_value.get('title', 'N/A')} - {sample_value.get('bedrooms', 0)}BR")
            else:
                print(f"   ⚠️  No results found")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Empty results
    print("\n4. Testing empty results:")
    try:
        response = requests.post(
            f"{base_url}/api/search/",
            json={
                "location": "NonExistentCity, XX",
                "limit": 5
            },
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            
            print(f"   ✅ Status: 200")
            print(f"   📊 Results type: {type(results).__name__}")
            print(f"   📊 Results count: {len(results)}")
            print(f"   📊 Total: {data.get('total', 0)}")
            
            if len(results) == 0:
                print(f"   ✅ Correctly returns empty dictionary")
            else:
                print(f"   ⚠️  Unexpected results found")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🎉 New response format testing completed!")

if __name__ == "__main__":
    test_new_response_format() 