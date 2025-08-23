#!/usr/bin/env python3
"""
Comprehensive foreign key setup script for listings_v2 migration
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager

def setup_foreign_keys():
    """Complete foreign key setup for listings_v2 migration"""
    try:
        supabase = SupabaseManager()
        
        print("🔗 Setting up foreign key relationships for listings_v2")
        print("=" * 60)
        
        # Step 1: Check current state
        print("\n📋 Step 1: Checking current foreign key relationships...")
        fk_query = """
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public'
            AND (tc.table_name = 'listings' OR tc.table_name = 'listings_v2')
        ORDER BY tc.table_name, kcu.column_name;
        """
        
        try:
            result = supabase.client.postgrest.rpc('exec_sql', {'sql': fk_query}).execute()
            
            listings_fks = [fk for fk in result.data if fk['table_name'] == 'listings']
            listings_v2_fks = [fk for fk in result.data if fk['table_name'] == 'listings_v2']
            
            print(f"   - listings table: {len(listings_fks)} foreign key(s)")
            print(f"   - listings_v2 table: {len(listings_v2_fks)} foreign key(s)")
            
        except Exception as e:
            print(f"   ⚠️  Could not check foreign keys: {str(e)}")
        
        # Step 2: Ensure listings_v2 table exists
        print("\n🏗️  Step 2: Ensuring listings_v2 table exists...")
        try:
            result = supabase.client.table("listings_v2").select("*").limit(1).execute()
            print("   ✅ listings_v2 table exists and is accessible")
        except Exception as e:
            print(f"   ❌ listings_v2 table not accessible: {str(e)}")
            print("   📝 Please create the listings_v2 table first using create_listings_v2_with_fk.py")
            return False
        
        # Step 3: Add foreign key to listings_v2 if needed
        print("\n🔗 Step 3: Setting up foreign key for listings_v2...")
        if not listings_v2_fks:
            add_fk_sql = """
            ALTER TABLE listings_v2 
            ADD CONSTRAINT fk_listings_v2_host_id 
            FOREIGN KEY (host_id) 
            REFERENCES profiles(id) 
            ON DELETE CASCADE;
            """
            
            try:
                response = supabase.client.postgrest.rpc('exec_sql', {'sql': add_fk_sql}).execute()
                print("   ✅ Foreign key constraint added to listings_v2")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("   ℹ️  Foreign key constraint already exists")
                else:
                    print(f"   ❌ Error adding foreign key constraint: {str(e)}")
                    return False
        else:
            print("   ✅ Foreign key constraint already exists in listings_v2")
        
        # Step 4: Remove foreign keys from old listings table (optional)
        if listings_fks:
            print(f"\n🗑️  Step 4: Removing foreign keys from old listings table...")
            response = input("   ❓ Do you want to remove foreign key constraints from the old listings table? (y/N): ")
            
            if response.lower() == 'y':
                remove_fk_sql = """
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (
                        SELECT conname
                        FROM pg_constraint
                        WHERE conrelid = 'listings'::regclass
                        AND contype = 'f'
                    ) LOOP
                        EXECUTE 'ALTER TABLE listings DROP CONSTRAINT ' || quote_ident(r.conname);
                        RAISE NOTICE 'Dropped constraint: %', r.conname;
                    END LOOP;
                END $$;
                """
                
                try:
                    response = supabase.client.postgrest.rpc('exec_sql', {'sql': remove_fk_sql}).execute()
                    print("   ✅ Foreign key constraints removed from listings table")
                except Exception as e:
                    print(f"   ⚠️  Could not remove foreign key constraints: {str(e)}")
            else:
                print("   ℹ️  Skipping removal of old foreign key constraints")
        else:
            print("   ℹ️  No foreign key constraints found in old listings table")
        
        # Step 5: Verify final state
        print("\n✅ Step 5: Verifying final foreign key setup...")
        try:
            result = supabase.client.postgrest.rpc('exec_sql', {'sql': fk_query}).execute()
            
            listings_fks = [fk for fk in result.data if fk['table_name'] == 'listings']
            listings_v2_fks = [fk for fk in result.data if fk['table_name'] == 'listings_v2']
            
            print(f"   📊 Final state:")
            print(f"      - listings table: {len(listings_fks)} foreign key(s)")
            print(f"      - listings_v2 table: {len(listings_v2_fks)} foreign key(s)")
            
            if listings_v2_fks:
                print("   ✅ listings_v2 table has proper foreign key relationships")
                for fk in listings_v2_fks:
                    print(f"      - {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
            
            print("\n🎉 Foreign key setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Error verifying final state: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Error in foreign key setup: {str(e)}")
        return False

def test_foreign_key_integrity():
    """Test foreign key integrity by creating a test listing"""
    try:
        supabase = SupabaseManager()
        
        print("\n🧪 Testing foreign key integrity...")
        
        # Get a valid host ID
        try:
            hosts_result = supabase.client.table("profiles").select("id").limit(1).execute()
            if not hosts_result.data:
                print("   ❌ No hosts found in profiles table")
                return False
            
            test_host_id = hosts_result.data[0]['id']
            print(f"   ✅ Found test host: {test_host_id}")
            
        except Exception as e:
            print(f"   ❌ Error getting test host: {str(e)}")
            return False
        
        # Create a test listing
        test_listing = {
            "host_id": test_host_id,
            "property_type": "Apartment",
            "property_listing_type": "rent",
            "title": "Test Listing for FK",
            "description": "Test description",
            "bedrooms": 2,
            "bathrooms": 1,
            "square_feet": 1000,
            "price_per_month": 2000,
            "city": "Test City",
            "state": "TS",
            "country": "United States",
            "latitude": 0.0,
            "longitude": 0.0,
            "address": "123 Test St",
            "neighborhood": "Test Neighborhood",
            "amenities": ["WiFi", "Kitchen"],
            "is_available": True,
            "is_featured": False,
            "embedding_text": ""
        }
        
        try:
            result = supabase.client.table("listings_v2").insert(test_listing).execute()
            if result.data:
                listing_id = result.data[0]['id']
                print(f"   ✅ Test listing created successfully: {listing_id}")
                
                # Clean up test listing
                supabase.client.table("listings_v2").delete().eq("id", listing_id).execute()
                print("   ✅ Test listing cleaned up")
                
                return True
            else:
                print("   ❌ Failed to create test listing")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating test listing: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Error in foreign key integrity test: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        success = test_foreign_key_integrity()
    else:
        success = setup_foreign_keys()
    
    sys.exit(0 if success else 1)
