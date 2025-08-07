#!/usr/bin/env python3
"""
Test script to verify full listing objects are returned correctly
"""

import requests
import json

def test_full_listing_objects():
    """Test that full listing objects are returned with all required fields"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Full Listing Objects")
    print("=" * 50)
    
    # Required fields from the requirements
    required_fields = [
        'id', 'title', 'description', 'property_type', 'property_listing_type',
        'bedrooms', 'bathrooms', 'square_feet', 'garage_number', 
        'price_per_night', 'price_per_month', 'price_for_sale',
        'city', 'state', 'country', 'latitude', 'longitude', 
        'address', 'neighborhood', 'has_yard', 'has_parking_lot', 
        'amenities', 'images', 'is_available', 'is_featured', 
        'rating', 'review_count'
    ]
    
    # Test 1: Search endpoint (POST)
    print("\n1. Testing /api/search endpoint (POST):")
    try:
        response = requests.post(
            f"{base_url}/api/search/",
            json={"limit": 1},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            
            print(f"   ✅ Status: 200")
            print(f"   📊 Results count: {len(results)}")
            print(f"   📊 Total: {data.get('total', 0)}")
            
            if results:
                # Get the first listing
                first_listing = list(results.values())[0]
                listing_id = list(results.keys())[0]
                
                print(f"   🔑 Listing ID: {listing_id}")
                print(f"   🏠 Title: {first_listing.get('title', 'N/A')}")
                print(f"   📍 Location: {first_listing.get('city', 'N/A')}, {first_listing.get('state', 'N/A')}")
                print(f"   🛏️  {first_listing.get('bedrooms', 0)}BR, 🚿 {first_listing.get('bathrooms', 0)}BA")
                print(f"   🏠 {first_listing.get('square_feet', 0)} sqft")
                print(f"   🏷️  Type: {first_listing.get('property_type', 'N/A')} ({first_listing.get('property_listing_type', 'N/A')})")
                
                # Check for required fields
                missing_fields = [field for field in required_fields if field not in first_listing]
                if missing_fields:
                    print(f"   ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present")
                
                # Show some key values
                print(f"   💰 Price per night: ${first_listing.get('price_per_night', 0):,.2f}")
                print(f"   💰 Price per month: ${first_listing.get('price_per_month', 0):,.2f}" if first_listing.get('price_per_month') else "   💰 Price per month: N/A")
                print(f"   💰 Price for sale: ${first_listing.get('price_for_sale', 0):,.2f}" if first_listing.get('price_for_sale') else "   💰 Price for sale: N/A")
                print(f"   🚗 Garage: {first_listing.get('garage_number', 0)} spaces")
                print(f"   🌳 Has yard: {first_listing.get('has_yard', False)}")
                print(f"   🅿️  Has parking: {first_listing.get('has_parking_lot', False)}")
                print(f"   ⭐ Rating: {first_listing.get('rating', 0)} ({first_listing.get('review_count', 0)} reviews)")
                print(f"   🏠 Available: {first_listing.get('is_available', False)}")
                print(f"   ⭐ Featured: {first_listing.get('is_featured', False)}")
                print(f"   🏠 Amenities: {len(first_listing.get('amenities', []))} items")
                print(f"   🖼️  Images: {len(first_listing.get('images', []))} images")
            else:
                print(f"   ⚠️  No results found")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Listings endpoint (GET)
    print("\n2. Testing /api/listings endpoint (GET):")
    try:
        response = requests.get(f"{base_url}/api/listings/?limit=1")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            
            print(f"   ✅ Status: 200")
            print(f"   📊 Results count: {len(results)}")
            print(f"   📊 Total: {data.get('total', 0)}")
            
            if results:
                # Get the first listing
                first_listing = list(results.values())[0]
                listing_id = list(results.keys())[0]
                
                print(f"   🔑 Listing ID: {listing_id}")
                print(f"   🏠 Title: {first_listing.get('title', 'N/A')}")
                
                # Check for required fields
                missing_fields = [field for field in required_fields if field not in first_listing]
                if missing_fields:
                    print(f"   ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present")
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
                "rent": "For Rent",
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
                # Verify all results have 2+ bedrooms and are for rent
                all_valid = all(
                    results[key].get('bedrooms', 0) >= 2 and 
                    results[key].get('property_listing_type') in ['rent', 'both']
                    for key in results.keys()
                )
                print(f"   ✅ All results have 2+ bedrooms and are for rent: {all_valid}")
                
                # Show sample
                sample_key = list(results.keys())[0]
                sample_value = results[sample_key]
                print(f"   🏠 Sample: {sample_value.get('title', 'N/A')} - {sample_value.get('bedrooms', 0)}BR")
                print(f"   🏷️  Type: {sample_value.get('property_listing_type', 'N/A')}")
            else:
                print(f"   ⚠️  No results found")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Pagination
    print("\n4. Testing pagination:")
    try:
        response = requests.post(
            f"{base_url}/api/search/",
            json={
                "page": 2,
                "limit": 3
            },
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            
            print(f"   ✅ Status: 200")
            print(f"   📊 Results count: {len(results)}")
            print(f"   📊 Page: {data.get('page', 0)}")
            print(f"   📊 Limit: {data.get('limit', 0)}")
            print(f"   📊 Total: {data.get('total', 0)}")
            print(f"   📊 Has more: {data.get('has_more', False)}")
            
            if results:
                print(f"   ✅ Pagination working correctly")
            else:
                print(f"   ⚠️  No results on page 2")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🎉 Full listing objects testing completed!")

if __name__ == "__main__":
    test_full_listing_objects() 