#!/usr/bin/env python3
"""
Fetch high-quality house images without API key
Uses curated high-quality image URLs for real estate
"""

import json
import requests
from typing import List
import random

class HighQualityImageFetcher:
    """Fetch high-quality images without API key"""
    
    def __init__(self):
        # Curated list of high-quality real estate images
        self.house_images = [
            # Modern Houses
            "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1200&h=800&fit=crop",
            
            # Luxury Homes
            "https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&h=800&fit=crop",
            
            # Apartments & Condos
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=1200&h=800&fit=crop",
            
            # Interior Shots
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=800&fit=crop",
            
            # Exterior Views
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1200&h=800&fit=crop",
            
            # Kitchen & Living Areas
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=800&fit=crop",
            
            # Bedrooms & Bathrooms
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=800&fit=crop",
            
            # Garden & Outdoor
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1200&h=800&fit=crop",
            
            # Pool & Amenities
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=1200&h=800&fit=crop"
        ]
    
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
    
    def fetch_and_validate_images(self, count: int = 50) -> List[str]:
        """Fetch and validate high-quality images"""
        print("🔍 Validating high-quality image URLs...")
        
        valid_urls = []
        total_images = len(self.house_images)
        
        # Shuffle the images for variety
        shuffled_images = self.house_images.copy()
        random.shuffle(shuffled_images)
        
        for i, image_url in enumerate(shuffled_images[:count], 1):
            if self.validate_image_url(image_url):
                valid_urls.append(image_url)
                print(f"✅ Image {i}/{min(count, total_images)}: Valid")
            else:
                print(f"❌ Image {i}/{min(count, total_images)}: Invalid URL")
        
        print(f"🎉 Validation complete: {len(valid_urls)}/{min(count, total_images)} images are valid")
        return valid_urls
    
    def save_images_to_json(self, image_urls: List[str], filename: str = "house_images.json"):
        """Save valid image URLs to JSON file"""
        data = {
            "total_images": len(image_urls),
            "source": "Curated High-Quality Images",
            "images": image_urls,
            "metadata": {
                "source": "Unsplash (curated)",
                "validation": "Verified URLs",
                "usage": "For real estate listings",
                "note": "No API key required - using curated selection"
            }
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(image_urls)} images to {filename}")
    
    def fetch_house_images(self, count: int = 50) -> List[str]:
        """Main method to fetch and validate house images"""
        print("🏠 High-Quality House Image Fetcher (No API Key Required)")
        print("=" * 60)
        
        # Fetch and validate image URLs
        valid_urls = self.fetch_and_validate_images(count)
        
        if not valid_urls:
            print("❌ No valid images found")
            return []
        
        # Save to JSON file
        self.save_images_to_json(valid_urls)
        
        return valid_urls

def main():
    """Main function"""
    try:
        fetcher = HighQualityImageFetcher()
        image_urls = fetcher.fetch_house_images(50)
        
        if image_urls:
            print(f"\n🎉 Successfully fetched {len(image_urls)} high-quality house images!")
            print("📁 Images saved to house_images.json")
            print("🔄 Ready to assign to 2000 listings")
            print("💡 No API key required - using curated selection")
        else:
            print("❌ Failed to fetch valid images")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 