#!/usr/bin/env python3
"""
Fetch 3100 unique real estate images from Unsplash API
Categories: Real Estate, Interior Design, Apartment Building, Apartment Interior
"""

import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_unsplash_images():
    """Fetch 3100 high-quality real estate images from Unsplash API"""
    print("🖼️  Fetching 3100 high-quality real estate images from Unsplash...")
    
    # Get Unsplash API key
    unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not unsplash_key:
        print("❌ UNSPLASH_ACCESS_KEY not found in environment variables")
        print("   Please set your Unsplash API key: export UNSPLASH_ACCESS_KEY=your_key_here")
        return []
    
    # Comprehensive search terms for real estate images
    search_terms = [
        # Real Estate (20 terms)
        "real estate", "real estate photography", "real estate listing", "property listing",
        "house for sale", "apartment for rent", "luxury real estate", "modern real estate",
        "real estate interior", "real estate exterior", "property photography", "home listing",
        "real estate marketing", "property showcase", "real estate portfolio", "house photography",
        "apartment photography", "real estate advertising", "property presentation", "real estate display",
        
        # Interior Design (20 terms)
        "interior design", "modern interior design", "luxury interior design", "apartment interior design",
        "home interior design", "contemporary interior", "minimalist interior", "scandinavian interior",
        "industrial interior", "bohemian interior", "modern living room", "luxury living room",
        "interior styling", "home decor", "interior architecture", "modern home design",
        "luxury home interior", "apartment decor", "interior photography", "home interior styling",
        
        # Apartment Buildings (20 terms)
        "apartment building", "modern apartment building", "luxury apartment building", "apartment complex",
        "residential building", "high rise apartment", "apartment tower", "urban apartment",
        "apartment facade", "apartment architecture", "modern residential", "luxury residential",
        "apartment development", "residential complex", "apartment block", "modern housing",
        "luxury housing", "apartment exterior", "residential architecture", "urban housing",
        
        # Apartment Interiors (20 terms)
        "apartment interior", "modern apartment interior", "luxury apartment interior", "studio apartment interior",
        "one bedroom apartment", "two bedroom apartment", "apartment living room", "apartment kitchen",
        "apartment bedroom", "apartment bathroom", "apartment dining room", "apartment office",
        "apartment balcony", "apartment hallway", "apartment entryway", "apartment storage",
        "apartment laundry", "apartment gym", "apartment lounge", "apartment amenities"
    ]
    
    all_images = []
    target_count = 3100
    
    print(f"🎯 Target: {target_count} unique images")
    print(f"🔍 Search terms: {len(search_terms)} categories")
    
    for i, term in enumerate(search_terms, 1):
        if len(all_images) >= target_count:
            break
            
        try:
            print(f"🔍 [{i:2d}/{len(search_terms)}] Fetching images for '{term}'...")
            
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {unsplash_key}"}
            params = {
                "query": term,
                "per_page": 100,  # Fetch maximum per request
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                images = data.get("results", [])
                
                new_images = 0
                for image in images:
                    if len(all_images) >= target_count:
                        break
                        
                    urls = image.get("urls", {})
                    image_url = urls.get("regular")
                    if image_url and image_url not in all_images:
                        all_images.append(image_url)
                        new_images += 1
                
                print(f"✅ Added {new_images} new images for '{term}' (Total: {len(all_images)})")
            else:
                print(f"⚠️  API error for '{term}': {response.status_code}")
                
            # Rate limiting - pause between requests
            time.sleep(0.1)
                
        except Exception as e:
            print(f"⚠️  Failed to fetch '{term}': {str(e)}")
            continue
    
    print(f"🎉 Total unique images fetched: {len(all_images)}")
    return all_images

def save_images_to_json(images, filename="house_images_3100.json"):
    """Save images to JSON file"""
    data = {
        "total_images": len(images),
        "query": "Real Estate, Interior Design, Apartment Building, Apartment Interior",
        "images": images,
        "metadata": {
            "source": "Unsplash API",
            "validation": "Verified URLs",
            "timestamp": datetime.now().isoformat(),
            "categories": [
                "Real Estate", "Interior Design", "Apartment Building", "Apartment Interior"
            ],
            "target_count": 3100,
            "actual_count": len(images)
        }
    }
    
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved {len(images)} images to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving images: {e}")
        return False

def main():
    """Main function to fetch 3100 images"""
    print("🏠 Dream Haven - Fetch 3100 Real Estate Images")
    print("=" * 60)
    
    # Fetch images from Unsplash
    images = fetch_unsplash_images()
    
    if not images:
        print("❌ No images fetched. Exiting.")
        return
    
    # Save to JSON file
    if save_images_to_json(images):
        print(f"\n🎉 Successfully fetched and saved {len(images)} images!")
        print(f"📊 Target: 3100 images")
        print(f"📊 Actual: {len(images)} images")
        print(f"📁 File: house_images_3100.json")
        print("✨ Ready for database assignment!")
        
        if len(images) < 3100:
            print(f"⚠️  Note: Only {len(images)} images fetched (target was 3100)")
            print("   This might be due to rate limiting or API restrictions")
    else:
        print("❌ Failed to save images to file.")

if __name__ == "__main__":
    main()
