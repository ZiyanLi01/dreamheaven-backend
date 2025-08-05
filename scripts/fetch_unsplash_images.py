#!/usr/bin/env python3
"""
Fetch high-quality house images from Unsplash API
Validate image URLs and save to JSON for reuse
"""

import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    
    def fetch_images(self, query: str = "house", count: int = 50) -> List[Dict[str, Any]]:
        """Fetch images from Unsplash API"""
        print(f"🔍 Fetching {count} images for query: '{query}'")
        
        url = f"{self.base_url}/search/photos"
        params = {
            "query": query,
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
            return images
            
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
                "usage": "For real estate listings"
            }
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(image_urls)} images to {filename}")
    
    def fetch_house_images(self, count: int = 50) -> List[str]:
        """Main method to fetch and validate house images"""
        print("🏠 Unsplash House Image Fetcher")
        print("=" * 40)
        
        # Fetch images from Unsplash
        images = self.fetch_images("house", count)
        
        if not images:
            print("❌ No images fetched from Unsplash")
            return []
        
        # Extract and validate image URLs
        valid_urls = self.extract_and_validate_images(images)
        
        if not valid_urls:
            print("❌ No valid images found")
            return []
        
        # Save to JSON file
        self.save_images_to_json(valid_urls)
        
        return valid_urls

def main():
    """Main function"""
    try:
        fetcher = UnsplashImageFetcher()
        image_urls = fetcher.fetch_house_images(50)
        
        if image_urls:
            print(f"\n🎉 Successfully fetched {len(image_urls)} high-quality house images!")
            print("📁 Images saved to house_images.json")
            print("🔄 Ready to assign to 2000 listings")
        else:
            print("❌ Failed to fetch valid images")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 