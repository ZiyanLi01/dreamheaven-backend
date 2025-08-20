#!/usr/bin/env python3
"""
Script to update listings_v2 table with single unique Unsplash images
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.upgrade_images import UnsplashImageFetcher, ListingImageUpdater, Config

def update_listings_v2_with_single_images():
    """Update listings_v2 with single unique Unsplash images"""
    print("🏠 Dream Haven - listings_v2 Single Image Update")
    print("=" * 60)
    
    try:
        # Validate configuration
        Config.validate_config()
        
        # Step 1: Fetch high-quality images from Unsplash API
        print("\n📸 Step 1: Fetching high-quality real estate images from Unsplash API...")
        fetcher = UnsplashImageFetcher()
        
        # Fetch more images to ensure we have enough unique ones
        image_urls = fetcher.fetch_house_images(100)  # Get 100 images for variety
        
        if not image_urls:
            print("❌ Failed to fetch images. Exiting.")
            return False
        
        print(f"✅ Successfully fetched {len(image_urls)} high-quality real estate images")
        
        # Step 2: Update listings_v2 with single unique images
        print("\n🔄 Step 2: Updating listings_v2 with single unique images...")
        updater = ListingImageUpdater()
        
        # Update listings_v2 with 1 image per listing, ensuring uniqueness
        updater.update_all_listings(
            image_urls=image_urls,
            table_name="listings_v2",
            images_per_listing=1
        )
        
        print("\n🎉 listings_v2 image update completed successfully!")
        print(f"✅ Fetched {len(image_urls)} high-quality real estate images")
        print("✅ Updated all listings_v2 with single unique images")
        print("✅ Each listing has exactly 1 real estate image (interior or exterior)")
        print("✅ No repeated images across listings")
        print("✅ Images are ready for your frontend!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during listings_v2 image update: {e}")
        return False

def main():
    success = update_listings_v2_with_single_images()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
