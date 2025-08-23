#!/usr/bin/env python3
"""
Test script to verify listings_v2 table migration
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager
from scripts.data_generator import RealEstateDataGenerator

def test_listings_v2_migration():
    """Test the migration to listings_v2 table"""
    print("🧪 Testing listings_v2 table migration")
    print("=" * 50)
    
    try:
        # Initialize components
        supabase = SupabaseManager()
        generator = RealEstateDataGenerator()
        
        # Test 1: Check if listings_v2 table exists and is accessible
        print("\n📋 Test 1: Checking listings_v2 table accessibility...")
        try:
            result = supabase.client.table("listings_v2").select("*").limit(1).execute()
            print("✅ listings_v2 table is accessible")
            print(f"   Current records: {len(result.data) if result.data else 0}")
        except Exception as e:
            print(f"❌ Error accessing listings_v2 table: {str(e)}")
            return False
        
        # Test 2: Generate a test listing
        print("\n🏠 Test 2: Generating test listing...")
        test_host_id = "test-host-id-123"
        test_listing = generator.generate_listing_v2(test_host_id)
        
        print(f"✅ Generated test listing:")
        print(f"   Title: {test_listing.get('title')}")
        print(f"   Property Type: {test_listing.get('property_type')}")
        print(f"   Listing Type: {test_listing.get('property_listing_type')}")
        print(f"   Price (Monthly): ${test_listing.get('price_per_month')}")
        print(f"   Price (Sale): ${test_listing.get('price_for_sale')}")
        print(f"   Bedrooms: {test_listing.get('bedrooms')}")
        print(f"   Bathrooms: {test_listing.get('bathrooms')}")
        print(f"   Square Feet: {test_listing.get('square_feet')}")
        print(f"   Has Yard: {test_listing.get('has_yard')}")
        print(f"   Has Parking: {test_listing.get('has_parking_lot')}")
        
        # Test 3: Create the test listing in the database
        print("\n💾 Test 3: Creating test listing in database...")
        try:
            created_listing = supabase.create_listing(test_listing)
            print("✅ Test listing created successfully")
            print(f"   Listing ID: {created_listing.get('id')}")
        except Exception as e:
            print(f"❌ Error creating test listing: {str(e)}")
            return False
        
        # Test 4: Retrieve the listing
        print("\n📖 Test 4: Retrieving test listing...")
        try:
            retrieved_listing = supabase.client.table("listings_v2").select("*").eq("id", created_listing.get('id')).execute()
            if retrieved_listing.data:
                print("✅ Test listing retrieved successfully")
                print(f"   Retrieved Title: {retrieved_listing.data[0].get('title')}")
            else:
                print("❌ Could not retrieve test listing")
                return False
        except Exception as e:
            print(f"❌ Error retrieving test listing: {str(e)}")
            return False
        
        # Test 5: Clean up test data
        print("\n🧹 Test 5: Cleaning up test data...")
        try:
            supabase.client.table("listings_v2").delete().eq("id", created_listing.get('id')).execute()
            print("✅ Test data cleaned up successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up test data: {str(e)}")
        
        print("\n🎉 All tests passed! listings_v2 table migration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_listings_v2_migration()
    sys.exit(0 if success else 1)

