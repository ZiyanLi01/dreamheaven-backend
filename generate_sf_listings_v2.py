#!/usr/bin/env python3
"""
Generate 20 San Francisco listings for listings table with v2 schema data
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager
from scripts.data_generator import RealEstateDataGenerator

def generate_sf_listings_v2():
    """Generate 20 San Francisco listings with v2 schema data"""
    try:
        # Initialize managers
        supabase = SupabaseManager()
        data_generator = RealEstateDataGenerator()
        
        print("🏠 Generating 20 San Francisco listings with v2 schema...")
        
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
        
        # Generate 20 San Francisco listings using v2 method
        listings = data_generator.generate_listings_v2(host_ids, 20)
        
        # Restore original cities
        data_generator.cities = original_cities
        
        # Insert into listings_v2 table
        print(f"📝 Inserting {len(listings)} listings into listings_v2 table...")
        
        # Insert in batches
        batch_size = 5
        for i in range(0, len(listings), batch_size):
            batch = listings[i:i + batch_size]
            result = supabase.client.table("listings_v2").insert(batch).execute()
            
            if result.data:
                print(f"✅ Inserted batch {i//batch_size + 1}: {len(result.data)} listings")
            else:
                print(f"❌ No data returned for batch {i//batch_size + 1}")
        
        print(f"🎉 Successfully inserted {len(listings)} San Francisco listings!")
        print("📍 All listings are located in San Francisco, CA")
        print("🏢 Table: listings_v2")
        print("📊 Count: 20 listings")
        print("✨ Features: Enhanced data with new fields, relaxed validation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating listings: {str(e)}")
        return False

if __name__ == "__main__":
    generate_sf_listings_v2()
