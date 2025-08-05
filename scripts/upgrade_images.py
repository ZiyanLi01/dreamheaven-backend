#!/usr/bin/env python3
"""
Comprehensive image upgrade script
1. Fetch high-quality images from Unsplash API
2. Validate all image URLs
3. Update existing listings with verified images
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.fetch_unsplash_images import UnsplashImageFetcher
from scripts.update_listings_with_images import ListingImageUpdater

def main():
    """Main function to upgrade all images"""
    print("🏠 Dream Haven - Image Quality Upgrade")
    print("=" * 50)
    
    try:
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