#!/usr/bin/env python3
"""
Update image URLs in existing listings to use more reliable image services
"""

import sys
import os
import random
from typing import List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager

def generate_better_images(property_type: str) -> List[str]:
    """Generate better image URLs"""
    num_images = random.randint(3, 8)
    images = []
    
    for i in range(num_images):
        width = random.choice([800, 1200, 1600])
        height = random.choice([600, 800, 1200])
        # Use Lorem Picsum with specific IDs that work
        image_id = random.randint(1, 100)
        images.append(f"https://picsum.photos/{width}/{height}?random={image_id}")
    
    return images

def update_listing_images():
    """Update all listings with better image URLs"""
    print("🖼️  Updating listing images...")
    
    try:
        Config.validate_config()
        supabase = SupabaseManager()
        
        # Get all listings (handle pagination)
        all_listings = []
        offset = 0
        limit = 1000
        
        while True:
            result = supabase.client.table("listings").select("id, property_type").range(offset, offset + limit - 1).execute()
            
            if not result.data:
                break
                
            all_listings.extend(result.data)
            offset += limit
            
            if len(result.data) < limit:
                break
        
        listings = all_listings
        
        if not result.data:
            print("❌ No listings found")
            return
        
        listings = result.data
        print(f"📊 Found {len(listings)} listings to update")
        
        # Update each listing
        updated_count = 0
        for listing in listings:
            try:
                new_images = generate_better_images(listing["property_type"])
                
                # Update the listing
                update_result = supabase.client.table("listings").update({
                    "images": new_images
                }).eq("id", listing["id"]).execute()
                
                if update_result.data:
                    updated_count += 1
                    if updated_count % 100 == 0:
                        print(f"✅ Updated {updated_count} listings...")
                
            except Exception as e:
                print(f"❌ Error updating listing {listing['id']}: {str(e)}")
                continue
        
        print(f"🎉 Successfully updated {updated_count} out of {len(listings)} listings")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_listing_images() 