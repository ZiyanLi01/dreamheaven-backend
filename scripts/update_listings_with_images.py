#!/usr/bin/env python3
"""
Update existing listings with high-quality Unsplash images
Load images from house_images.json and assign to 2000 listings
"""

import json
import sys
import os
from typing import List, Dict, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager

class ListingImageUpdater:
    """Update listings with high-quality images"""
    
    def __init__(self):
        self.supabase = SupabaseManager()
        self.image_urls = []
    
    def load_images_from_json(self, filename: str = "house_images.json") -> List[str]:
        """Load image URLs from JSON file"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            
            image_urls = data.get("images", [])
            print(f"📁 Loaded {len(image_urls)} images from {filename}")
            return image_urls
            
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please run fetch_unsplash_images.py first.")
            return []
        except Exception as e:
            print(f"❌ Error loading images: {e}")
            return []
    
    def generate_listing_images(self, image_urls: List[str], num_images: int = 5) -> List[str]:
        """Generate a list of images for a listing by cycling through available images"""
        if not image_urls:
            return []
        
        # Randomly select images from the pool
        import random
        selected_images = []
        
        for i in range(num_images):
            # Cycle through images with some randomness
            image_index = (i + random.randint(0, len(image_urls) - 1)) % len(image_urls)
            selected_images.append(image_urls[image_index])
        
        return selected_images
    
    def update_listing_images(self, listing_id: str, images: List[str]) -> bool:
        """Update a single listing with new images"""
        try:
            result = self.supabase.client.table("listings").update({
                "images": images
            }).eq("id", listing_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            print(f"❌ Error updating listing {listing_id}: {e}")
            return False
    
    def update_all_listings(self, image_urls: List[str]):
        """Update all listings with high-quality images"""
        print("🖼️  Updating listings with high-quality images...")
        
        try:
            # Get all listings
            result = self.supabase.client.table("listings").select("id").execute()
            
            if not result.data:
                print("❌ No listings found")
                return
            
            listings = result.data
            total_listings = len(listings)
            print(f"📊 Found {total_listings} listings to update")
            
            # Update each listing
            updated_count = 0
            for i, listing in enumerate(listings, 1):
                try:
                    # Generate 3-8 images for each listing
                    import random
                    num_images = random.randint(3, 8)
                    listing_images = self.generate_listing_images(image_urls, num_images)
                    
                    # Update the listing
                    if self.update_listing_images(listing["id"], listing_images):
                        updated_count += 1
                        
                        if updated_count % 100 == 0:
                            print(f"✅ Updated {updated_count}/{total_listings} listings...")
                    
                except Exception as e:
                    print(f"❌ Error updating listing {listing['id']}: {e}")
                    continue
            
            print(f"🎉 Successfully updated {updated_count}/{total_listings} listings")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def create_sample_listings_json(self, image_urls: List[str], num_listings: int = 2000):
        """Create sample listings JSON with high-quality images (for testing)"""
        print(f"📝 Creating {num_listings} sample listings with high-quality images...")
        
        import random
        from faker import Faker
        
        fake = Faker()
        listings = []
        
        property_types = ["House", "Apartment", "Condo", "Townhouse", "Villa"]
        cities = ["San Francisco", "New York", "Los Angeles", "Chicago", "Miami"]
        
        for i in range(num_listings):
            # Generate 3-8 images for each listing
            num_images = random.randint(3, 8)
            listing_images = self.generate_listing_images(image_urls, num_images)
            
            listing = {
                "id": fake.uuid4(),
                "title": f"{random.choice(property_types)} in {random.choice(cities)}",
                "price": random.randint(100000, 2000000),
                "property_type": random.choice(property_types),
                "city": random.choice(cities),
                "images": listing_images
            }
            
            listings.append(listing)
        
        # Save to JSON file
        data = {
            "total_listings": len(listings),
            "total_images_used": len(image_urls),
            "listings": listings
        }
        
        with open("listings_with_images.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(listings)} listings to listings_with_images.json")
        print(f"🖼️  Used {len(image_urls)} unique images ({(len(listings) * 5) / len(image_urls):.1f}x reuse)")

def main():
    """Main function"""
    print("🏠 Listing Image Updater")
    print("=" * 30)
    
    try:
        updater = ListingImageUpdater()
        
        # Load images from JSON
        image_urls = updater.load_images_from_json()
        
        if not image_urls:
            print("❌ No images loaded. Please run fetch_unsplash_images.py first.")
            return
        
        # Ask user what to do
        print("\nWhat would you like to do?")
        print("1. Update existing listings in database")
        print("2. Create sample listings JSON file")
        print("3. Both")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice in ["1", "3"]:
            # Update existing listings
            updater.update_all_listings(image_urls)
        
        if choice in ["2", "3"]:
            # Create sample listings
            updater.create_sample_listings_json(image_urls)
        
        print("\n🎉 Image update process completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 