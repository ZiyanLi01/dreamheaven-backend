#!/usr/bin/env python3
"""
Script to check the actual number of listings in the database
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager

def check_listing_count():
    """Check the actual number of listings in the database"""
    print("🔍 Checking Database Listing Count")
    print("=" * 40)
    
    try:
        supabase = SupabaseManager()
        
        # Get all listings
        result = supabase.client.table("listings").select("id").execute()
        
        if result.data:
            total_count = len(result.data)
            print(f"📊 Total listings in database: {total_count}")
            
            # Check by type
            type_result = supabase.client.table("listings").select("property_listing_type").execute()
            if type_result.data:
                from collections import Counter
                type_counts = Counter([item['property_listing_type'] for item in type_result.data])
                print(f"\n📋 Distribution by type:")
                for listing_type, count in type_counts.items():
                    print(f"   - {listing_type}: {count} properties")
            
            # Check by city
            city_result = supabase.client.table("listings").select("city").execute()
            if city_result.data:
                city_counts = Counter([item['city'] for item in city_result.data])
                print(f"\n🏙️  Distribution by city:")
                for city, count in city_counts.most_common():
                    print(f"   - {city}: {count} properties")
            
            # Check amenities
            yard_result = supabase.client.table("listings").select("has_yard").eq("has_yard", True).execute()
            parking_result = supabase.client.table("listings").select("has_parking_lot").eq("has_parking_lot", True).execute()
            
            print(f"\n🏡 Amenities summary:")
            print(f"   - Properties with yards: {len(yard_result.data) if yard_result.data else 0}")
            print(f"   - Properties with parking lots: {len(parking_result.data) if parking_result.data else 0}")
            
        else:
            print("❌ No listings found in database")
            
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")

if __name__ == "__main__":
    check_listing_count() 