#!/usr/bin/env python3
"""
Test script for the new filtered listings endpoint.
This script tests the GET /api/listings endpoint with various filters.
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_listings_endpoint(params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test the listings endpoint with given parameters"""
    url = f"{BASE_URL}/api/listings"
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def print_response(response: Dict[str, Any], test_name: str):
    """Print the response in a formatted way"""
    print(f"\n📋 {test_name}")
    print("-" * 50)
    
    if response:
        print(f"✅ Status: Success")
        print(f"📄 Total listings: {response.get('total', 0)}")
        print(f"📄 Current page: {response.get('page', 0)}")
        print(f"📄 Limit per page: {response.get('limit', 0)}")
        print(f"📄 Has more pages: {response.get('has_more', False)}")
        print(f"📄 Results count: {len(response.get('results', []))}")
        
        # Show first few results
        results = response.get('results', [])
        if results:
            print(f"\n🏠 Sample listings:")
            for i, listing in enumerate(results[:3], 1):
                print(f"   {i}. {listing.get('address', 'N/A')} - {listing.get('status', 'N/A')}")
                print(f"      💰 ${listing.get('price', 0):,.2f} | 🛏️ {listing.get('bedrooms', 0)}BR | 🚿 {listing.get('bathrooms', 0)}BA")
                print(f"      📍 {listing.get('location', 'N/A')} | 👤 {listing.get('agent', 'N/A')}")
                print(f"      📅 {listing.get('listingAge', 'N/A')}")
                print()
    else:
        print("❌ No response received")

def main():
    """Run all tests"""
    print("🏠 Dream Haven Backend - Listings Endpoint Tests")
    print("=" * 60)
    
    # Test 1: Basic endpoint without filters
    print("\n🧪 Test 1: Basic endpoint (no filters)")
    response = test_listings_endpoint()
    print_response(response, "Basic endpoint test")
    
    # Test 2: Pagination
    print("\n🧪 Test 2: Pagination (page 1, limit 5)")
    response = test_listings_endpoint({"page": 1, "limit": 5})
    print_response(response, "Pagination test")
    
    # Test 3: Location filter
    print("\n🧪 Test 3: Location filter")
    response = test_listings_endpoint({"location": "New York"})
    print_response(response, "Location filter test")
    
    # Test 4: Bedrooms filter
    print("\n🧪 Test 4: Bedrooms filter (2 bedrooms)")
    response = test_listings_endpoint({"bedrooms": 2})
    print_response(response, "Bedrooms filter test")
    
    # Test 5: Bathrooms filter
    print("\n🧪 Test 5: Bathrooms filter (2 bathrooms)")
    response = test_listings_endpoint({"bathrooms": 2})
    print_response(response, "Bathrooms filter test")
    
    # Test 6: Status filter
    print("\n🧪 Test 6: Status filter (For Sale)")
    response = test_listings_endpoint({"status": "For Sale"})
    print_response(response, "Status filter test (For Sale)")
    
    print("\n🧪 Test 6b: Status filter (For Rent)")
    response = test_listings_endpoint({"status": "For Rent"})
    print_response(response, "Status filter test (For Rent)")
    
    # Test 7: Combined filters
    print("\n🧪 Test 7: Combined filters")
    response = test_listings_endpoint({
        "location": "Los Angeles",
        "bedrooms": 3,
        "bathrooms": 2,
        "status": "For Sale",
        "page": 1,
        "limit": 10
    })
    print_response(response, "Combined filters test")
    
    # Test 8: Edge cases
    print("\n🧪 Test 8: Edge cases")
    
    # Test with non-existent location
    response = test_listings_endpoint({"location": "NonExistentCity"})
    print_response(response, "Non-existent location test")
    
    # Test with high page number
    response = test_listings_endpoint({"page": 999, "limit": 10})
    print_response(response, "High page number test")
    
    print("\n🎉 All tests completed!")
    print("\n📝 To run these tests, make sure:")
    print("   1. The backend server is running (python main.py)")
    print("   2. The database migration has been applied (python scripts/run_migration.py)")
    print("   3. There is sample data in the database")

if __name__ == "__main__":
    main() 