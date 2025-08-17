#!/usr/bin/env python3
"""
Clear title, description, and images from listings_v2 table
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager

def clear_listings_content():
    """Clear title, description, and images from all listings in listings_v2"""
    try:
        supabase = SupabaseManager()
        
        print("🧹 Clearing title, description, and images from listings_v2...")
        
        # First, let's see how many listings we have
        result = supabase.client.table("listings_v2").select("id").execute()
        total_listings = len(result.data) if result.data else 0
        
        print(f"📊 Found {total_listings} listings in listings_v2 table")
        
        if total_listings == 0:
            print("ℹ️  No listings found to update")
            return True
        
        # Update all listings to clear title, description, and images
        update_data = {
            "title": "",
            "description": "",
            "images": None
        }
        
        # Get all listing IDs first
        listings_result = supabase.client.table("listings_v2").select("id").execute()
        listing_ids = [listing["id"] for listing in listings_result.data] if listings_result.data else []
        
        print(f"🔄 Updating {len(listing_ids)} listings...")
        
        # Update each listing individually
        updated_count = 0
        for listing_id in listing_ids:
            try:
                result = supabase.client.table("listings_v2").update(update_data).eq("id", listing_id).execute()
                if result.data:
                    updated_count += 1
                    print(f"✅ Updated listing {updated_count}/{len(listing_ids)}")
            except Exception as e:
                print(f"❌ Failed to update listing {listing_id}: {str(e)}")
                continue
        
        print(f"✅ Successfully cleared content from {updated_count} listings!")
        print("📝 Updated fields:")
        print("   - title: '' (empty string)")
        print("   - description: '' (empty string)")
        print("   - images: null")
        
        if updated_count == 0:
            print("❌ No listings were updated")
            return False
        
        # Verify the update
        print("\n🔍 Verifying the update...")
        sample_result = supabase.client.table("listings_v2").select("id, title, description, images").limit(3).execute()
        
        if sample_result.data:
            print("📋 Sample updated listings:")
            for i, listing in enumerate(sample_result.data, 1):
                print(f"  Listing {i}:")
                print(f"    Title: '{listing.get('title', '')}'")
                print(f"    Description: '{listing.get('description', '')}'")
                print(f"    Images: {listing.get('images')}")
        else:
            print("❌ Could not verify the update")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing listings content: {str(e)}")
        return False

if __name__ == "__main__":
    clear_listings_content()
