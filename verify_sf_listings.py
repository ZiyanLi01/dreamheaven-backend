#!/usr/bin/env python3
"""
Verify San Francisco listings generation
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager

def verify_sf_listings():
    """Verify San Francisco listings were generated"""
    try:
        supabase = SupabaseManager()
        
        # Get San Francisco listings from listings_v2
        result = supabase.client.table("listings_v2").select("*").eq("city", "San Francisco").execute()
        
        print(f"✅ Successfully generated {len(result.data)} San Francisco listings!")
        
        if result.data:
            print("\n📋 Sample listing details:")
            sample = result.data[0]
            print(f"  Title: {sample.get('title', 'Untitled')}")
            print(f"  Property Type: {sample.get('property_type')}")
            print(f"  Property Listing Type: {sample.get('property_listing_type')}")
            print(f"  Bedrooms: {sample.get('bedrooms')}")
            print(f"  Bathrooms: {sample.get('bathrooms')}")
            print(f"  Square Feet: {sample.get('square_feet')}")
            print(f"  Price per Month: ${sample.get('price_per_month')}")
            print(f"  Price for Sale: ${sample.get('price_for_sale')}")
            print(f"  Neighborhood: {sample.get('neighborhood')}")
            print(f"  Has Yard: {sample.get('has_yard')}")
            print(f"  Has Parking: {sample.get('has_parking_lot')}")
            print(f"  Rating: {sample.get('rating')}")
            print(f"  Review Count: {sample.get('review_count')}")
            print(f"  Amenities: {sample.get('amenities')}")
            
            # Check for v2 schema features
            print(f"\n✨ V2 Schema Features:")
            print(f"  - Relaxed validation: Title can be empty: {sample.get('title') == ''}")
            print(f"  - Separate pricing: Monthly: {sample.get('price_per_month')}, Sale: {sample.get('price_for_sale')}")
            print(f"  - Enhanced data: Rating: {sample.get('rating')}, Reviews: {sample.get('review_count')}")
            print(f"  - Property features: Yard: {sample.get('has_yard')}, Parking: {sample.get('has_parking_lot')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying listings: {str(e)}")
        return False

if __name__ == "__main__":
    verify_sf_listings()
