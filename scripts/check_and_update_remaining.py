#!/usr/bin/env python3
"""
Check and update any remaining listings that need image updates
"""

import json
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager

def main():
    """Check and update remaining listings"""
    print("🔍 Checking for remaining listings that need image updates...")
    
    try:
        supabase = SupabaseManager()
        
        # Load the high-quality images
        with open("house_images.json", "r") as f:
            data = json.load(f)
            image_urls = data.get("images", [])
        
        print(f"📁 Loaded {len(image_urls)} high-quality images")
        
        # Get total count of listings
        count_result = supabase.client.table("listings").select("id", count="exact").execute()
        total_listings = count_result.count
        print(f"📊 Total listings in database: {total_listings}")
        
        # Get all listings with pagination
        all_listings = []
        page = 0
        page_size = 1000
        
        while True:
            result = supabase.client.table("listings").select("id, images").range(page * page_size, (page + 1) * page_size - 1).execute()
            
            if not result.data:
                break
            
            all_listings.extend(result.data)
            page += 1
            
            if len(result.data) < page_size:
                break
        
        print(f"📋 Retrieved {len(all_listings)} listings")
        
        # Check which listings need updates (those with old placeholder images)
        listings_to_update = []
        for listing in all_listings:
            images = listing.get("images", [])
            # Check if images are old placeholder URLs (picsum.photos)
            needs_update = False
            if not images:
                needs_update = True
            else:
                for img in images:
                    if "picsum.photos" in img:
                        needs_update = True
                        break
            
            if needs_update:
                listings_to_update.append(listing["id"])
        
        print(f"🔄 Found {len(listings_to_update)} listings that need image updates")
        
        if listings_to_update:
            print("🖼️  Updating remaining listings...")
            
            # Update the listings
            updated_count = 0
            import random
            
            for i, listing_id in enumerate(listings_to_update, 1):
                try:
                    # Generate 1 image for each listing
                    listing_images = []
                    
                    # Select 1 random image
                    image_index = random.randint(0, len(image_urls) - 1)
                    listing_images.append(image_urls[image_index])
                    
                    # Update the listing
                    result = supabase.client.table("listings").update({
                        "images": listing_images
                    }).eq("id", listing_id).execute()
                    
                    if result.data:
                        updated_count += 1
                        
                        if updated_count % 50 == 0:
                            print(f"✅ Updated {updated_count}/{len(listings_to_update)} listings...")
                    
                except Exception as e:
                    print(f"❌ Error updating listing {listing_id}: {e}")
                    continue
            
            print(f"🎉 Successfully updated {updated_count}/{len(listings_to_update)} remaining listings")
        else:
            print("✅ All listings already have high-quality images!")
        
        # Final count check
        final_count = supabase.client.table("listings").select("id", count="exact").execute()
        print(f"📊 Final count: {final_count.count} listings in database")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 