#!/usr/bin/env python3
"""
Dream Haven Data Generation Script
Creates fake hosts and listings for the real estate platform
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import Config
from scripts.data_generator import RealEstateDataGenerator
from scripts.supabase_manager import SupabaseManager

def main():
    """Main function to generate and upload data"""
    print("🏠 Dream Haven Data Generation")
    print("=" * 50)
    
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize components
        generator = RealEstateDataGenerator()
        supabase = SupabaseManager()
        
        # Show database schema requirements
        supabase.create_database_schema()
        
        # Get configuration
        num_hosts = Config.NUM_HOSTS
        num_listings = Config.NUM_LISTINGS
        
        print(f"\n📊 Configuration:")
        print(f"   - Number of hosts: {num_hosts}")
        print(f"   - Number of listings: {num_listings}")
        
        # Ask for confirmation
        response = input("\n❓ Do you want to proceed with data generation? (y/N): ")
        if response.lower() != 'y':
            print("❌ Data generation cancelled.")
            return
        
        # Step 1: Generate and create hosts
        print(f"\n👥 Step 1: Creating {num_hosts} hosts...")
        hosts_data = generator.generate_hosts(num_hosts)
        
        created_hosts = supabase.create_users_batch(hosts_data)
        
        if not created_hosts:
            print("❌ No hosts were created. Exiting.")
            return
        
        # Extract host IDs for listings
        host_ids = [host["auth_user"].id for host in created_hosts if host.get("auth_user")]
        
        if not host_ids:
            print("❌ No valid host IDs found. Exiting.")
            return
        
        print(f"✅ Successfully created {len(created_hosts)} hosts")
        
        # Step 2: Generate and create listings
        print(f"\n🏘️  Step 2: Creating {num_listings} listings...")
        listings_data = generator.generate_listings(host_ids, num_listings)
        
        created_listings = supabase.create_listings_batch(listings_data)
        
        print(f"✅ Successfully created {len(created_listings)} listings")
        
        # Step 3: Generate summary report
        print(f"\n📈 Summary Report:")
        print(f"   - Hosts created: {len(created_hosts)}")
        print(f"   - Listings created: {len(created_listings)}")
        
        # Save data to JSON files for backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(f"data/hosts_{timestamp}.json", "w") as f:
            json.dump(hosts_data, f, indent=2, default=str)
        
        with open(f"data/listings_{timestamp}.json", "w") as f:
            json.dump(listings_data, f, indent=2, default=str)
        
        print(f"💾 Data saved to data/hosts_{timestamp}.json and data/listings_{timestamp}.json")
        
        print("\n🎉 Data generation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during data generation: {str(e)}")
        sys.exit(1)

def generate_hosts_only():
    """Generate only hosts (for testing)"""
    print("👥 Dream Haven - Host Generation Only")
    print("=" * 40)
    
    try:
        Config.validate_config()
        
        generator = RealEstateDataGenerator()
        supabase = SupabaseManager()
        
        num_hosts = Config.NUM_HOSTS
        print(f"Creating {num_hosts} hosts...")
        
        hosts_data = generator.generate_hosts(num_hosts)
        created_hosts = supabase.create_users_batch(hosts_data)
        
        print(f"✅ Successfully created {len(created_hosts)} hosts")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

def generate_listings_only():
    """Generate only listings (requires existing hosts)"""
    print("🏘️  Dream Haven - Listing Generation Only")
    print("=" * 40)
    
    try:
        Config.validate_config()
        
        generator = RealEstateDataGenerator()
        supabase = SupabaseManager()
        
        # Get existing hosts
        existing_hosts = supabase.get_all_users()
        if not existing_hosts:
            print("❌ No existing hosts found. Please create hosts first.")
            return
        
        host_ids = [host["id"] for host in existing_hosts]
        print(f"Found {len(host_ids)} existing hosts")
        
        num_listings = Config.NUM_LISTINGS
        print(f"Creating {num_listings} listings...")
        
        listings_data = generator.generate_listings(host_ids, num_listings)
        created_listings = supabase.create_listings_batch(listings_data)
        
        print(f"✅ Successfully created {len(created_listings)} listings")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

def cleanup_data():
    """Clean up all data (for testing)"""
    print("🧹 Dream Haven - Data Cleanup")
    print("=" * 30)
    
    try:
        Config.validate_config()
        supabase = SupabaseManager()
        
        response = input("⚠️  This will delete ALL listings. Are you sure? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cleanup cancelled.")
            return
        
        supabase.delete_all_data()
        print("✅ Data cleanup completed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "hosts":
            generate_hosts_only()
        elif command == "listings":
            generate_listings_only()
        elif command == "cleanup":
            cleanup_data()
        elif command == "help":
            print("Usage:")
            print("  python generate_data.py          # Generate hosts and listings")
            print("  python generate_data.py hosts    # Generate hosts only")
            print("  python generate_data.py listings # Generate listings only")
            print("  python generate_data.py cleanup  # Clean up all data")
            print("  python generate_data.py help     # Show this help")
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python generate_data.py help' for usage information")
    else:
        main() 