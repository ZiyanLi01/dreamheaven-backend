#!/usr/bin/env python3
"""
Generate San Francisco listings with specific average prices
- 2000 rental listings with average $3,500/month
- 1000 sale listings with average $1.2M
- Images will be assigned separately using upgrade_images.py
"""

import sys
import os
import random
import uuid
import json
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager
from scripts.data_generator import RealEstateDataGenerator

def generate_sf_listings_v2():
    """Generate SF listings with specific price targets"""
    try:
        # Initialize managers
        supabase = SupabaseManager()
        data_generator = RealEstateDataGenerator()
        
        # Images will be handled separately - leave as null for now
        print("🖼️  Images will be assigned separately - leaving as null")
        
        # Target prices
        target_rental_avg = 3500
        target_sale_avg = 1200000
        
        print("🏠 Generating San Francisco listings with specific price targets...")
        print(f"📊 Target average rental price: ${target_rental_avg:,}/month")
        print(f"📊 Target average sale price: ${target_sale_avg:,}")
        print("-" * 80)
        
        # Get host IDs
        try:
            hosts_result = supabase.client.table("profiles").select("id").limit(10).execute()
            host_ids = [host["id"] for host in hosts_result.data] if hosts_result.data else []
            
            if not host_ids:
                print("⚠️  No hosts found, creating demo hosts...")
                demo_hosts = data_generator.generate_hosts(5)
                hosts_result = supabase.client.table("profiles").insert(demo_hosts).execute()
                host_ids = [host["id"] for host in hosts_result.data] if hosts_result.data else []
                
        except Exception as e:
            print(f"❌ Error getting hosts: {str(e)}")
            host_ids = ["550e8400-e29b-41d4-a716-446655440003"]
        
        # Override cities to only use San Francisco
        original_cities = data_generator.cities
        data_generator.cities = [
            {
                "name": "San Francisco",
                "state": "CA",
                "lat": 37.7749,
                "lng": -122.4194
            }
        ]
        
        # Generate 2000 rental listings
        print("🏢 Generating 2000 rental listings...")
        rental_listings = []
        
        for i in range(2000):
            # Generate base listing
            listing = data_generator.generate_listing_v2(random.choice(host_ids))
            
            # Ensure fresh UUID for this listing
            listing["id"] = str(uuid.uuid4())
            
            # Force it to be a rental property
            listing["property_listing_type"] = "rent"
            listing["price_for_sale"] = None
            
            # Generate realistic rental price around $3,500 average
            base_rental = target_rental_avg
            variation = random.uniform(0.7, 1.3)  # ±30% variation
            rental_price = int(base_rental * variation)
            
            listing["price_per_month"] = rental_price
            listing["price_for_sale"] = None
            
            # Images will be assigned separately
            listing["images"] = None
            
            # Update title to reflect it's a rental
            listing["title"] = f"Beautiful {listing['property_type']} for Rent in {listing['neighborhood']}"
            
            rental_listings.append(listing)
            if (i + 1) % 100 == 0:
                print(f"  ✅ Generated {i+1:4d}/2000 rentals - ${rental_price:,}/month - {listing['neighborhood']}")
        
        # Generate 1000 sale listings
        print("\n🏠 Generating 1000 sale listings...")
        sale_listings = []
        
        for i in range(1000):
            # Generate base listing
            listing = data_generator.generate_listing_v2(random.choice(host_ids))
            
            # Ensure fresh UUID for this listing
            listing["id"] = str(uuid.uuid4())
            
            # Force it to be a sale property
            listing["property_listing_type"] = "sale"
            listing["price_per_month"] = None
            
            # Generate realistic sale price around $1.2M average
            base_sale = target_sale_avg
            variation = random.uniform(0.8, 1.4)  # ±30% variation
            sale_price = int(base_sale * variation)
            
            listing["price_for_sale"] = sale_price
            listing["price_per_month"] = None
            
            # Images will be assigned separately
            listing["images"] = None
            
            # Update title to reflect it's for sale
            listing["title"] = f"Beautiful {listing['property_type']} for Sale in {listing['neighborhood']}"
            
            sale_listings.append(listing)
            if (i + 1) % 100 == 0:
                print(f"  ✅ Generated {i+1:4d}/1000 sales - ${sale_price:,} - {listing['neighborhood']}")
        
        # Combine all listings
        all_listings = rental_listings + sale_listings
        
        # Calculate actual averages
        rental_prices = [l["price_per_month"] for l in rental_listings if l["price_per_month"]]
        sale_prices = [l["price_for_sale"] for l in sale_listings if l["price_for_sale"]]
        
        actual_rental_avg = sum(rental_prices) / len(rental_prices) if rental_prices else 0
        actual_sale_avg = sum(sale_prices) / len(sale_prices) if sale_prices else 0
        
        print("\n" + "=" * 80)
        print("📊 PRICE SUMMARY:")
        print(f"🏢 Rental Listings: {len(rental_listings)}")
        print(f"   Target Average: ${target_rental_avg:,}/month")
        print(f"   Actual Average: ${actual_rental_avg:,.0f}/month")
        print(f"   Price Range: ${min(rental_prices):,} - ${max(rental_prices):,}")
        
        print(f"\n🏠 Sale Listings: {len(sale_listings)}")
        print(f"   Target Average: ${target_sale_avg:,}")
        print(f"   Actual Average: ${actual_sale_avg:,.0f}")
        print(f"   Price Range: ${min(sale_prices):,} - ${max(sale_prices):,}")
        
        print(f"\n📈 Total Listings: {len(all_listings)}")
        print("🖼️  Images will be assigned separately")
        print("=" * 80)
        
        # Restore original cities
        data_generator.cities = original_cities
        
        # Insert into listings_v2 table
        print(f"\n💾 Inserting {len(all_listings)} listings into listings_v2 table...")
        
        # Insert in batches
        batch_size = 50  # Increased batch size for better performance
        for i in range(0, len(all_listings), batch_size):
            batch = all_listings[i:i + batch_size]
            result = supabase.client.table("listings_v2").insert(batch).execute()
            
            if result.data:
                print(f"✅ Inserted batch {i//batch_size + 1}: {len(result.data)} listings")
            else:
                print(f"❌ No data returned for batch {i//batch_size + 1}")
            
            # Show progress every 10 batches
            if (i//batch_size + 1) % 10 == 0:
                print(f"📊 Progress: {i + len(result.data)}/{len(all_listings)} listings inserted...")
        
        print(f"\n🎉 Successfully inserted {len(all_listings)} San Francisco listings!")
        print("📍 All listings are located in San Francisco, CA")
        print("🏢 Table: listings_v2")
        print(f"📊 Count: {len(all_listings)} listings ({len(rental_listings)} rentals, {len(sale_listings)} sales)")
        print("✨ Features: Enhanced data with specific price targets")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating listings: {str(e)}")
        return False

if __name__ == "__main__":
    generate_sf_listings_v2()
