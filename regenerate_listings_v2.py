#!/usr/bin/env python3
"""
Remove existing listings from listings_v2, regenerate 20 new listings with current methods, and insert them
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager
from scripts.data_generator import RealEstateDataGenerator

def regenerate_listings_v2():
    """Remove existing listings and regenerate 20 new ones with current methods"""
    try:
        # Initialize managers
        supabase = SupabaseManager()
        data_generator = RealEstateDataGenerator()
        
        print("🗑️  Removing existing listings from listings_v2...")
        
        # Delete all existing listings from listings_v2
        try:
            result = supabase.client.table("listings_v2").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print(f"✅ Successfully removed existing listings from listings_v2")
        except Exception as e:
            print(f"❌ Error removing existing listings: {str(e)}")
            return False
        
        print("\n🏠 Generating 20 new San Francisco listings with current methods...")
        
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
        
        # Generate 20 new San Francisco listings using current methods
        listings = data_generator.generate_listings_v2(host_ids, 20)
        
        # Restore original cities
        data_generator.cities = original_cities
        
        # Insert into listings_v2 table
        print(f"\n📝 Inserting {len(listings)} new listings into listings_v2 table...")
        
        # Insert in batches
        batch_size = 5
        for i in range(0, len(listings), batch_size):
            batch = listings[i:i + batch_size]
            result = supabase.client.table("listings_v2").insert(batch).execute()
            
            if result.data:
                print(f"✅ Inserted batch {i//batch_size + 1}: {len(result.data)} listings")
            else:
                print(f"❌ No data returned for batch {i//batch_size + 1}")
        
        print(f"\n🎉 Successfully regenerated and inserted {len(listings)} new San Francisco listings!")
        print("📍 All listings are located in San Francisco, CA")
        print("🏢 Table: listings_v2")
        print("📊 Count: 20 listings")
        print("✨ Features:")
        print("   - ChatGPT-generated descriptions")
        print("   - Proper titles using _generate_title")
        print("   - Enhanced v2 schema data")
        print("   - All new fields populated")
        
        return True
        
    except Exception as e:
        print(f"❌ Error regenerating listings: {str(e)}")
        return False

if __name__ == "__main__":
    regenerate_listings_v2()
