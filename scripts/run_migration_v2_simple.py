#!/usr/bin/env python3
"""
Simplified migration script for Supabase that adds new fields to listings table.
This version works around Supabase's limitations by using direct operations.
"""

import sys
import os
from pathlib import Path
import random

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.supabase_manager import SupabaseManager

def add_new_fields():
    """Add new fields to existing listings using Supabase operations"""
    print("🔄 Adding new fields to listings table...")
    
    try:
        supabase = SupabaseManager()
        
        # Get all existing listings
        result = supabase.client.table("listings").select("*").execute()
        
        if not result.data:
            print("⚠️  No listings found in database")
            return False
        
        listings = result.data
        print(f"📊 Found {len(listings)} listings to update")
        
        # Update each listing with new fields
        updated_count = 0
        
        for listing in listings:
            try:
                # Determine property listing type based on property_type
                property_type = listing.get('property_type', 'House')
                if property_type in ['Apartment', 'Studio']:
                    property_listing_type = 'rent'
                elif property_type in ['House', 'Condo', 'Townhouse', 'Villa', 'Penthouse', 'Duplex', 'Cottage']:
                    property_listing_type = 'sale'
                else:
                    property_listing_type = 'sale'
                
                # Set some properties as both (10% chance)
                if property_type in ['House', 'Condo', 'Townhouse'] and random.random() < 0.1:
                    property_listing_type = 'both'
                
                # Calculate prices
                price_per_night = float(listing.get('price_per_night', 0))
                price_for_sale = None
                price_per_month = None
                
                if property_listing_type in ['sale', 'both']:
                    price_for_sale = price_per_night * 30 * 12  # Convert to annual sale price
                
                if property_listing_type in ['rent', 'both']:
                    price_per_month = price_per_night * 30  # Convert to monthly rent
                
                # Set garage number based on property type and size
                square_feet = listing.get('square_feet', 0)
                if property_type in ['House', 'Villa']:
                    garage_number = 2 if square_feet > 2000 else 1
                elif property_type in ['Condo', 'Townhouse']:
                    garage_number = 1
                else:
                    garage_number = 0
                
                # Set yard availability
                has_yard = property_type in ['House', 'Villa', 'Cottage'] or (
                    property_type == 'Townhouse' and random.random() < 0.7
                )
                
                # Set parking lot availability
                has_parking_lot = property_type in ['Apartment', 'Condo', 'Studio'] or (
                    property_type in ['House', 'Villa'] and random.random() < 0.3
                )
                
                # Update the listing
                update_data = {
                    'property_listing_type': property_listing_type,
                    'price_for_sale': price_for_sale,
                    'price_per_month': price_per_month,
                    'garage_number': garage_number,
                    'has_yard': has_yard,
                    'has_parking_lot': has_parking_lot
                }
                
                # Remove None values
                update_data = {k: v for k, v in update_data.items() if v is not None}
                
                # Update the listing
                supabase.client.table("listings").update(update_data).eq("id", listing['id']).execute()
                updated_count += 1
                
                if updated_count % 100 == 0:
                    print(f"✅ Updated {updated_count} listings...")
                    
            except Exception as e:
                print(f"⚠️  Error updating listing {listing.get('id', 'unknown')}: {str(e)}")
                continue
        
        print(f"✅ Successfully updated {updated_count} out of {len(listings)} listings")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def verify_migration():
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
            print("\n📊 Data statistics:")
            
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
    print("🏠 Dream Haven Backend - Database Migration (Version 2 - Simple)")
    print("=" * 70)
    
    success = add_new_fields()
    
    if success:
        verify_migration()
        show_sample_data()
        print("\n🎉 Migration process completed successfully!")
        print("You can now use the enhanced listings API with new fields.")
    else:
        print("\n💥 Migration process failed!")
        sys.exit(1) 