#!/usr/bin/env python3
"""
Migration script to move data from listings table to listings_v2 table
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager

def migrate_to_listings_v2():
    """Migrate data from listings table to listings_v2 table"""
    print("🔄 Migrating from listings to listings_v2 table")
    print("=" * 60)
    
    try:
        # Initialize Supabase manager
        supabase = SupabaseManager()
        
        # Step 1: Check if listings_v2 table exists
        print("\n📋 Step 1: Checking listings_v2 table...")
        try:
            result = supabase.client.table("listings_v2").select("*").limit(1).execute()
            print("✅ listings_v2 table is accessible")
        except Exception as e:
            print(f"❌ Error accessing listings_v2 table: {str(e)}")
            print("📝 Please create the listings_v2 table first using create_listings_v2_direct.py")
            return False
        
        # Step 2: Get all data from old listings table
        print("\n📖 Step 2: Reading data from old listings table...")
        try:
            old_listings = supabase.client.table("listings").select("*").execute()
            if not old_listings.data:
                print("ℹ️  No data found in old listings table")
                return True
            
            print(f"✅ Found {len(old_listings.data)} listings in old table")
        except Exception as e:
            print(f"❌ Error reading from old listings table: {str(e)}")
            return False
        
        # Step 3: Transform and migrate data
        print("\n🔄 Step 3: Migrating data...")
        migrated_count = 0
        failed_count = 0
        
        for old_listing in old_listings.data:
            try:
                # Transform old listing to new format
                new_listing = {
                    "id": old_listing.get("id"),
                    "host_id": old_listing.get("host_id"),
                    "title": old_listing.get("title", ""),
                    "description": old_listing.get("description", ""),
                    "property_type": old_listing.get("property_type"),
                    "property_listing_type": old_listing.get("property_listing_type", "rent"),  # Default to rent
                    "bedrooms": old_listing.get("bedrooms"),
                    "bathrooms": old_listing.get("bathrooms"),
                    "square_feet": old_listing.get("square_feet"),
                    "price_per_month": old_listing.get("price_per_month"),
                    "price_for_sale": old_listing.get("price_for_sale"),
                    "city": old_listing.get("city"),
                    "state": old_listing.get("state"),
                    "country": old_listing.get("country", "United States"),
                    "latitude": old_listing.get("latitude"),
                    "longitude": old_listing.get("longitude"),
                    "address": old_listing.get("address"),
                    "neighborhood": old_listing.get("neighborhood"),
                    "garage_number": old_listing.get("garage_number"),
                    "has_yard": old_listing.get("has_yard", False),
                    "has_parking_lot": old_listing.get("has_parking_lot", False),
                    "amenities": old_listing.get("amenities", []),
                    "images": old_listing.get("images"),
                    "is_available": old_listing.get("is_available", True),
                    "is_featured": old_listing.get("is_featured", False),
                    "rating": old_listing.get("rating"),
                    "review_count": old_listing.get("review_count"),
                    "embedding_text": "",  # Will be populated later
                    "created_at": old_listing.get("created_at"),
                    "updated_at": old_listing.get("updated_at")
                }
                
                # Insert into new table
                result = supabase.client.table("listings_v2").insert(new_listing).execute()
                if result.data:
                    migrated_count += 1
                    print(f"✅ Migrated listing: {new_listing.get('title', 'Untitled')}")
                else:
                    failed_count += 1
                    print(f"❌ Failed to migrate listing: {new_listing.get('title', 'Untitled')}")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Error migrating listing {old_listing.get('id')}: {str(e)}")
                continue
        
        # Step 4: Summary
        print(f"\n📊 Migration Summary:")
        print(f"   - Total listings in old table: {len(old_listing.data)}")
        print(f"   - Successfully migrated: {migrated_count}")
        print(f"   - Failed migrations: {failed_count}")
        
        if migrated_count > 0:
            print(f"\n✅ Migration completed successfully!")
            print(f"   - {migrated_count} listings migrated to listings_v2 table")
            
            # Ask if user wants to delete old table
            response = input(f"\n❓ Do you want to delete the old listings table? (y/N): ")
            if response.lower() == 'y':
                try:
                    supabase.client.table("listings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                    print("✅ Old listings table data deleted")
                except Exception as e:
                    print(f"⚠️  Warning: Could not delete old table data: {str(e)}")
            else:
                print("ℹ️  Old listings table data preserved")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed with error: {str(e)}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    print("=" * 30)
    
    try:
        supabase = SupabaseManager()
        
        # Check old table
        old_count = 0
        try:
            old_result = supabase.client.table("listings").select("id", count="exact").execute()
            old_count = old_result.count if old_result.count else 0
        except:
            pass
        
        # Check new table
        new_result = supabase.client.table("listings_v2").select("id", count="exact").execute()
        new_count = new_result.count if new_result.count else 0
        
        print(f"📊 Verification Results:")
        print(f"   - Old listings table: {old_count} records")
        print(f"   - New listings_v2 table: {new_count} records")
        
        if new_count > 0:
            print("✅ Migration verification successful!")
            return True
        else:
            print("❌ No data found in new table")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        success = verify_migration()
    else:
        success = migrate_to_listings_v2()
    
    sys.exit(0 if success else 1)
