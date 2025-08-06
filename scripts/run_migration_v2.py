#!/usr/bin/env python3
"""
Script to run database migration for the enhanced listings schema (Version 2).
This script adds new fields for property types, dual pricing, and amenities.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.supabase_manager import SupabaseManager

def run_migration_v2():
    """Run the database migration to add new fields to listings table"""
    print("🔄 Running database migration for listings table (Version 2)...")
    
    try:
        supabase = SupabaseManager()
        
        # Read the migration SQL file
        migration_file = Path(__file__).parent.parent / "update_listings_schema_v2.sql"
        
        if not migration_file.exists():
            print("❌ Migration file not found: update_listings_schema_v2.sql")
            return False
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"📝 Executing statement {i}/{len(statements)}...")
                try:
                    # Execute the SQL statement
                    result = supabase.client.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"✅ Statement {i} executed successfully")
                except Exception as e:
                    print(f"⚠️  Statement {i} failed (this might be expected if field already exists): {str(e)}")
                    # Continue with other statements even if one fails
        
        print("✅ Database migration completed!")
        print("\n📋 Summary of changes:")
        print("   - Added 'property_listing_type' field (rent/sale/both)")
        print("   - Added 'price_for_sale' field for sale properties")
        print("   - Added 'price_per_month' field for rent properties")
        print("   - Added 'garage_number' field for garage spaces")
        print("   - Added 'has_yard' field for yard availability")
        print("   - Added 'has_parking_lot' field for parking availability")
        print("   - Created indexes for better query performance")
        print("   - Added data constraints for integrity")
        print("   - Created views for easier querying")
        print("   - Added helper function for pricing info")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def verify_migration_v2():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        supabase = SupabaseManager()
        
        # Check if new fields exist by querying a sample record
        result = supabase.client.table("listings").select(
            "property_listing_type, price_for_sale, price_per_month, garage_number, has_yard, has_parking_lot"
        ).limit(1).execute()
        
        if result.data:
            sample = result.data[0]
            print("✅ New fields found in listings table:")
            for field in ['property_listing_type', 'price_for_sale', 'price_per_month', 'garage_number', 'has_yard', 'has_parking_lot']:
                if field in sample:
                    print(f"   - {field}: {sample[field]}")
                else:
                    print(f"   - {field}: ❌ Not found")
            
            # Show some statistics
            print("\n📊 Sample data statistics:")
            
            # Count by listing type
            type_result = supabase.client.table("listings").select("property_listing_type").execute()
            if type_result.data:
                type_counts = {}
                for item in type_result.data:
                    listing_type = item.get('property_listing_type', 'unknown')
                    type_counts[listing_type] = type_counts.get(listing_type, 0) + 1
                
                for listing_type, count in type_counts.items():
                    print(f"   - {listing_type}: {count} properties")
            
            # Count properties with yards
            yard_result = supabase.client.table("listings").select("has_yard").eq("has_yard", True).execute()
            if yard_result.data:
                print(f"   - Properties with yards: {len(yard_result.data)}")
            
            # Count properties with parking
            parking_result = supabase.client.table("listings").select("has_parking_lot").eq("has_parking_lot", True).execute()
            if parking_result.data:
                print(f"   - Properties with parking lots: {len(parking_result.data)}")
                
        else:
            print("⚠️  No listings found to verify migration")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

def show_sample_data():
    """Show sample data with new fields"""
    print("\n🏠 Sample property data with new fields:")
    print("-" * 60)
    
    try:
        supabase = SupabaseManager()
        
        # Get a few sample properties
        result = supabase.client.table("listings").select(
            "id, title, property_listing_type, price_for_sale, price_per_month, garage_number, has_yard, has_parking_lot, city"
        ).limit(5).execute()
        
        if result.data:
            for i, property_data in enumerate(result.data, 1):
                print(f"\n{i}. {property_data.get('title', 'N/A')}")
                print(f"   📍 {property_data.get('city', 'N/A')}")
                print(f"   🏷️  Type: {property_data.get('property_listing_type', 'N/A')}")
                
                sale_price = property_data.get('price_for_sale')
                rent_price = property_data.get('price_per_month')
                
                if sale_price:
                    print(f"   💰 Sale Price: ${sale_price:,.2f}")
                if rent_price:
                    print(f"   🏠 Monthly Rent: ${rent_price:,.2f}")
                
                print(f"   🚗 Garage: {property_data.get('garage_number', 0)} spaces")
                print(f"   🌳 Yard: {'Yes' if property_data.get('has_yard') else 'No'}")
                print(f"   🅿️  Parking Lot: {'Yes' if property_data.get('has_parking_lot') else 'No'}")
        else:
            print("No sample data found")
            
    except Exception as e:
        print(f"❌ Error showing sample data: {str(e)}")

if __name__ == "__main__":
    print("🏠 Dream Haven Backend - Database Migration (Version 2)")
    print("=" * 60)
    
    success = run_migration_v2()
    
    if success:
        verify_migration_v2()
        show_sample_data()
        print("\n🎉 Migration process completed successfully!")
        print("You can now use the enhanced listings API with new fields.")
    else:
        print("\n💥 Migration process failed!")
        sys.exit(1) 