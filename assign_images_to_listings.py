#!/usr/bin/env python3
"""
Assign unique images from 3100 image pool to all listings in listings_v2 table
"""

import sys
import os
import json
import random
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager

def load_image_pool(filename="house_images_3100.json"):
    """Load the image pool from JSON file"""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            images = data.get("images", [])
            print(f"✅ Loaded {len(images)} images from {filename}")
            return images
    except FileNotFoundError:
        print(f"❌ {filename} not found")
        return []
    except Exception as e:
        print(f"❌ Error loading images: {e}")
        return []

def get_all_listings(supabase):
    """Get all listings from listings_v2 table"""
    print("📊 Fetching all listings from listings_v2 table...")
    
    all_listings = []
    page = 0
    page_size = 1000
    
    while True:
        try:
            result = supabase.client.table("listings_v2").select("id, title, neighborhood").range(
                page * page_size, (page + 1) * page_size - 1
            ).execute()
            
            if not result.data:
                break
            
            all_listings.extend(result.data)
            page += 1
            
            print(f"📄 Fetched page {page}: {len(result.data)} listings")
            
            # If we got less than page_size, we've reached the end
            if len(result.data) < page_size:
                break
                
        except Exception as e:
            print(f"❌ Error fetching listings: {e}")
            break
    
    print(f"📈 Total listings found: {len(all_listings)}")
    return all_listings

def assign_unique_images(listings, image_pool):
    """Assign unique images to listings"""
    print("🖼️  Assigning unique images to listings...")
    
    if len(image_pool) < len(listings):
        print(f"⚠️  Warning: Only {len(image_pool)} images available for {len(listings)} listings")
        print("   Some images will be reused")
    
    # Create a copy of the image pool to track usage
    available_images = image_pool.copy()
    used_images = set()
    assignments = []
    
    for i, listing in enumerate(listings):
        listing_id = listing["id"]
        title = listing.get("title", "Untitled")
        neighborhood = listing.get("neighborhood", "Unknown")
        
        # If we run out of unique images, reset the pool
        if not available_images:
            available_images = image_pool.copy()
            used_images.clear()
            print("🔄 Reset image pool - some images will be reused")
        
        # Select a random image from available pool
        selected_image = random.choice(available_images)
        available_images.remove(selected_image)  # Remove from available pool
        used_images.add(selected_image)  # Track usage
        
        assignments.append({
            "id": listing_id,
            "images": [selected_image],
            "title": title,
            "neighborhood": neighborhood
        })
        
        # Show progress every 100 assignments
        if (i + 1) % 100 == 0:
            print(f"✅ Assigned {i + 1:4d}/{len(listings)} images")
    
    print(f"🎉 Image assignment complete: {len(assignments)} listings")
    print(f"🖼️  Unique images used: {len(used_images)}")
    
    return assignments

def update_listings_in_database(supabase, assignments):
    """Update listings in database with assigned images"""
    print("💾 Updating listings in database...")
    
    batch_size = 50
    updated_count = 0
    failed_count = 0
    
    for i in range(0, len(assignments), batch_size):
        batch = assignments[i:i + batch_size]
        
        try:
            # Update each listing in the batch
            for assignment in batch:
                result = supabase.client.table("listings_v2").update({
                    "images": assignment["images"]
                }).eq("id", assignment["id"]).execute()
                
                if result.data:
                    updated_count += 1
                else:
                    failed_count += 1
                    print(f"❌ Failed to update listing {assignment['id']}")
            
            # Show progress every 10 batches
            if (i//batch_size + 1) % 10 == 0:
                print(f"📊 Progress: {i + len(batch)}/{len(assignments)} listings updated...")
                
        except Exception as e:
            print(f"❌ Error updating batch {i//batch_size + 1}: {e}")
            failed_count += len(batch)
    
    print(f"\n🎉 Database update complete!")
    print(f"✅ Successfully updated: {updated_count} listings")
    if failed_count > 0:
        print(f"❌ Failed to update: {failed_count} listings")
    
    return updated_count, failed_count

def main():
    """Main function to assign images to listings"""
    print("🏠 Dream Haven - Assign Images to Listings")
    print("=" * 50)
    
    try:
        # Initialize Supabase
        supabase = SupabaseManager()
        
        # Load image pool
        image_pool = load_image_pool()
        if not image_pool:
            print("❌ No images loaded. Exiting.")
            return
        
        # Get all listings
        listings = get_all_listings(supabase)
        if not listings:
            print("❌ No listings found. Exiting.")
            return
        
        # Assign unique images
        assignments = assign_unique_images(listings, image_pool)
        
        # Update database
        updated_count, failed_count = update_listings_in_database(supabase, assignments)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 ASSIGNMENT SUMMARY:")
        print(f"🏢 Total Listings: {len(listings)}")
        print(f"🖼️  Images Available: {len(image_pool)}")
        print(f"✅ Successfully Updated: {updated_count}")
        if failed_count > 0:
            print(f"❌ Failed Updates: {failed_count}")
        print(f"🎯 Coverage: {updated_count/len(listings)*100:.1f}%")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during image assignment: {e}")

if __name__ == "__main__":
    main()
