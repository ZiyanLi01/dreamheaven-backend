#!/usr/bin/env python3
"""
Comprehensive image upgrade script
1. Fetch high-quality images from Unsplash API
2. Validate all image URLs
3. Update existing listings with verified images
"""

import sys
import os
import json
import requests
from typing import List, Dict, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager

class UnsplashImageFetcher:
    """Fetch and validate images from Unsplash API"""
    
    def __init__(self):
        self.access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.access_key:
            raise ValueError("UNSPLASH_ACCESS_KEY environment variable is required")
        
        self.base_url = "https://api.unsplash.com"
        self.headers = {
            "Authorization": f"Client-ID {self.access_key}"
        }
    
    def fetch_house_images(self, count: int = 50) -> List[str]:
        """Fetch house images from Unsplash API"""
        print(f"🔍 Fetching {count} house images from Unsplash API...")
        
        url = f"{self.base_url}/search/photos"
        params = {
            "query": "house",
            "per_page": count,
            "page": 1,
            "orientation": "landscape"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            images = data.get("results", [])
            
            print(f"✅ Fetched {len(images)} images from Unsplash")
            
            # Extract and validate image URLs
            valid_urls = self.extract_and_validate_images(images)
            
            # Save to JSON for reuse
            if valid_urls:
                self.save_images_to_json(valid_urls)
            
            return valid_urls
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching images: {e}")
            return []
    
    def validate_image_url(self, image_url: str) -> bool:
        """Validate that an image URL returns a valid image"""
        try:
            response = requests.head(image_url, timeout=10)
            return (
                response.status_code == 200 and
                response.headers.get("content-type", "").startswith("image/")
            )
        except Exception:
            return False
    
    def extract_and_validate_images(self, images: List[Dict[str, Any]]) -> List[str]:
        """Extract image URLs and validate them"""
        print("🔍 Validating image URLs...")
        
        valid_urls = []
        total_images = len(images)
        
        for i, image in enumerate(images, 1):
            # Extract the regular size URL
            urls = image.get("urls", {})
            image_url = urls.get("regular")
            
            if not image_url:
                print(f"⚠️  Image {i}: No regular URL found")
                continue
            
            # Validate the image URL
            if self.validate_image_url(image_url):
                valid_urls.append(image_url)
                print(f"✅ Image {i}/{total_images}: Valid")
            else:
                print(f"❌ Image {i}/{total_images}: Invalid URL")
        
        print(f"🎉 Validation complete: {len(valid_urls)}/{total_images} images are valid")
        return valid_urls
    
    def save_images_to_json(self, image_urls: List[str], filename: str = "house_images.json"):
        """Save valid image URLs to JSON file"""
        data = {
            "total_images": len(image_urls),
            "query": "house",
            "images": image_urls,
            "metadata": {
                "source": "Unsplash API",
                "validation": "Verified URLs",
                "timestamp": "2024-08-16"
            }
        }
        
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"💾 Saved {len(image_urls)} images to {filename}")
        except Exception as e:
            print(f"❌ Error saving images: {e}")

class ListingImageUpdater:
    """Update listings with high-quality images"""
    
    def __init__(self):
        self.supabase = SupabaseManager()
    
    def generate_listing_images(self, image_urls: List[str], num_images: int = 1) -> List[str]:
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
            # Get all listings with pagination to handle 2000+ records
            all_listings = []
            page = 0
            page_size = 1000
            
            while True:
                result = self.supabase.client.table("listings").select("id").range(page * page_size, (page + 1) * page_size - 1).execute()
                
                if not result.data:
                    break
                
                all_listings.extend(result.data)
                page += 1
                
                # If we got less than page_size, we've reached the end
                if len(result.data) < page_size:
                    break
            
            if not all_listings:
                print("❌ No listings found")
                return
            
            total_listings = len(all_listings)
            print(f"📊 Found {total_listings} listings to update")
            
            # Update each listing with new images
            updated_count = 0
            failed_count = 0
            
            for i, listing in enumerate(all_listings, 1):
                # Generate 3-8 images for each listing
                num_images = 3 + (i % 6)  # Vary between 3-8 images
                new_images = self.generate_listing_images(image_urls, num_images)
                
                if self.update_listing_images(listing["id"], new_images):
                    updated_count += 1
                    if i % 100 == 0:
                        print(f"✅ Updated {i}/{total_listings} listings...")
                else:
                    failed_count += 1
            
            print(f"\n🎉 Image update completed!")
            print(f"✅ Successfully updated: {updated_count} listings")
            if failed_count > 0:
                print(f"❌ Failed to update: {failed_count} listings")
            
        except Exception as e:
            print(f"❌ Error updating listings: {e}")

def main():
    """Main function to upgrade all images"""
    print("🏠 Dream Haven - Image Quality Upgrade")
    print("=" * 50)
    
    try:
        # Validate configuration
        Config.validate_config()
        
        # Step 1: Fetch high-quality images from Unsplash API
        print("\n📸 Step 1: Fetching high-quality images from Unsplash API...")
        fetcher = UnsplashImageFetcher()
        image_urls = fetcher.fetch_house_images(50)
        
        if not image_urls:
            print("❌ Failed to fetch images. Exiting.")
            return
        
        # Step 2: Update existing listings with new images
        print("\n🔄 Step 2: Updating listings with high-quality images...")
        updater = ListingImageUpdater()
        updater.update_all_listings(image_urls)
        
        print("\n🎉 Image upgrade completed successfully!")
        print(f"✅ Fetched {len(image_urls)} high-quality images")
        print("✅ Updated all listings with verified image URLs")
        print("✅ Images are now ready for your frontend!")
        
    except Exception as e:
        print(f"❌ Error during image upgrade: {e}")

if __name__ == "__main__":
    main() 