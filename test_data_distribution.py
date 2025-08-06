#!/usr/bin/env python3
"""
Test script to check data distribution and new fields
"""

import requests
import json
from collections import Counter

def test_data_distribution():
    """Test the data distribution and new fields"""
    print("🏠 Testing Data Distribution and New Fields")
    print("=" * 50)
    
    # Get sample data
    response = requests.get("http://localhost:8000/api/listings/?limit=100")
    data = response.json()
    
    if not data.get('results'):
        print("❌ No data found")
        return
    
    results = data['results']
    
    # Check listing types
    types = [item['listing_type'] for item in results]
    type_counts = Counter(types)
    print(f"📊 Listing Type Distribution:")
    for listing_type, count in type_counts.items():
        print(f"   - {listing_type}: {count} properties")
    
    # Check pricing
    print(f"\n💰 Pricing Analysis:")
    sale_prices = [item['price_for_sale'] for item in results if item['price_for_sale']]
    rent_prices = [item['price_per_month'] for item in results if item['price_per_month']]
    
    if sale_prices:
        print(f"   - Sale prices: ${min(sale_prices):,.0f} - ${max(sale_prices):,.0f}")
    if rent_prices:
        print(f"   - Rent prices: ${min(rent_prices):,.0f} - ${max(rent_prices):,.0f}")
    
    # Check amenities
    print(f"\n🏡 Amenities Analysis:")
    yards = sum(1 for item in results if item['has_yard'])
    parking = sum(1 for item in results if item['has_parking_lot'])
    garages = [item['garages'] for item in results]
    
    print(f"   - Properties with yards: {yards}/{len(results)} ({yards/len(results)*100:.1f}%)")
    print(f"   - Properties with parking lots: {parking}/{len(results)} ({parking/len(results)*100:.1f}%)")
    print(f"   - Garage spaces: {min(garages)}-{max(garages)} (avg: {sum(garages)/len(garages):.1f})")
    
    # Show sample "both" type properties
    both_props = [item for item in results if item['listing_type'] == 'both']
    if both_props:
        print(f"\n🔄 Sample 'Both' Type Properties:")
        for i, prop in enumerate(both_props[:3], 1):
            print(f"   {i}. {prop['address']}")
            print(f"      💰 Sale: ${prop['price_for_sale']:,.0f}")
            print(f"      🏠 Rent: ${prop['price_per_month']:,.0f}")
            print(f"      🚗 Garage: {prop['garages']} spaces")
            print(f"      🌳 Yard: {'Yes' if prop['has_yard'] else 'No'}")
            print(f"      🅿️  Parking: {'Yes' if prop['has_parking_lot'] else 'No'}")
            print()
    
    # Test different filters
    print(f"🔍 Testing Filters:")
    
    # Test rent filter
    rent_response = requests.get("http://localhost:8000/api/listings/?status=For%20Rent&limit=5")
    rent_data = rent_response.json()
    print(f"   - Rent filter: {len(rent_data.get('results', []))} results")
    
    # Test sale filter
    sale_response = requests.get("http://localhost:8000/api/listings/?status=For%20Sale&limit=5")
    sale_data = sale_response.json()
    print(f"   - Sale filter: {len(sale_data.get('results', []))} results")
    
    # Test location filter
    la_response = requests.get("http://localhost:8000/api/listings/?location=Los%20Angeles&limit=5")
    la_data = la_response.json()
    print(f"   - LA filter: {len(la_data.get('results', []))} results")
    
    print(f"\n✅ Data generation and API testing completed successfully!")

if __name__ == "__main__":
    test_data_distribution() 