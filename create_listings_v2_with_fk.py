#!/usr/bin/env python3
"""
Create listings_v2 table with proper foreign key constraints
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager

def create_listings_v2_table_with_fk():
    """Create the listings_v2 table with foreign key constraints"""
    try:
        supabase = SupabaseManager()
        
        print("🚀 Creating listings_v2 table with foreign key constraints...")
        
        # Create the table with foreign key constraint
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS listings_v2 (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            host_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            property_type TEXT NOT NULL,
            property_listing_type TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            images JSONB DEFAULT NULL,
            bedrooms SMALLINT NOT NULL,
            bathrooms SMALLINT NOT NULL,
            square_feet INTEGER NOT NULL,
            price_per_month INTEGER NULL,
            price_for_sale INTEGER NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            country TEXT NOT NULL,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            address TEXT NOT NULL,
            neighborhood TEXT NOT NULL,
            garage_number SMALLINT NULL,
            has_yard BOOLEAN NOT NULL DEFAULT false,
            has_parking_lot BOOLEAN NOT NULL DEFAULT false,
            amenities TEXT[] NULL,
            is_available BOOLEAN NOT NULL DEFAULT true,
            is_featured BOOLEAN NOT NULL DEFAULT false,
            rating DOUBLE PRECISION NULL,
            review_count INTEGER NULL,
            floor INTEGER NULL,
            year_built SMALLINT NULL,
            year_renovated SMALLINT NULL,
            school_rating SMALLINT NULL,
            crime_index DOUBLE PRECISION NULL,
            facing TEXT NULL,
            shopping_idx DOUBLE PRECISION NULL,
            grocery_idx DOUBLE PRECISION NULL,
            tags TEXT[] NULL,
            embedding_text TEXT NOT NULL DEFAULT '',
            embedding VECTOR(1536) NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        """
        
        # Create indexes for better performance
        create_indexes_sql = """
        -- Index on host_id for foreign key lookups
        CREATE INDEX IF NOT EXISTS idx_listings_v2_host_id ON listings_v2(host_id);
        
        -- Index on property_type for filtering
        CREATE INDEX IF NOT EXISTS idx_listings_v2_property_type ON listings_v2(property_type);
        
        -- Index on property_listing_type for filtering
        CREATE INDEX IF NOT EXISTS idx_listings_v2_listing_type ON listings_v2(property_listing_type);
        
        -- Index on city and state for location filtering
        CREATE INDEX IF NOT EXISTS idx_listings_v2_location ON listings_v2(city, state);
        
        -- Index on price_per_month for sorting
        CREATE INDEX IF NOT EXISTS idx_listings_v2_price_month ON listings_v2(price_per_month);
        
        -- Index on price_for_sale for sorting
        CREATE INDEX IF NOT EXISTS idx_listings_v2_price_sale ON listings_v2(price_for_sale);
        
        -- Index on is_available for filtering
        CREATE INDEX IF NOT EXISTS idx_listings_v2_available ON listings_v2(is_available);
        
        -- Index on is_featured for filtering
        CREATE INDEX IF NOT EXISTS idx_listings_v2_featured ON listings_v2(is_featured);
        
        -- Composite index for common queries
        CREATE INDEX IF NOT EXISTS idx_listings_v2_common_query ON listings_v2(is_available, property_listing_type, city);
        """
        
        # Try using the raw SQL endpoint
        try:
            # Create the table
            response = supabase.client.postgrest.rpc('exec_sql', {'sql': create_table_sql}).execute()
            print("✅ listings_v2 table created using RPC")
            
            # Create indexes
            response = supabase.client.postgrest.rpc('exec_sql', {'sql': create_indexes_sql}).execute()
            print("✅ Indexes created successfully")
            
        except Exception as e:
            print(f"⚠️  RPC method failed: {str(e)}")
            
            # Try alternative approach - create table through Supabase dashboard
            print("📝 Please create the listings_v2 table manually in your Supabase dashboard:")
            print("   SQL to run in Supabase SQL Editor:")
            print(create_table_sql)
            print("\n   And then create the indexes:")
            print(create_indexes_sql)
            return False
        
        # Verify the table was created
        try:
            result = supabase.client.table("listings_v2").select("*").limit(1).execute()
            print("✅ listings_v2 table verified - exists and accessible")
            
            # Test foreign key constraint
            print("🔗 Testing foreign key constraint...")
            test_fk_sql = """
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
                AND tc.table_name='listings_v2';
            """
            
            try:
                fk_result = supabase.client.postgrest.rpc('exec_sql', {'sql': test_fk_sql}).execute()
                if fk_result.data:
                    print("✅ Foreign key constraint verified:")
                    for fk in fk_result.data:
                        print(f"   - {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                else:
                    print("⚠️  No foreign key constraints found")
            except Exception as e:
                print(f"⚠️  Could not verify foreign key constraints: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying table: {str(e)}")
            print("📝 Please create the listings_v2 table manually in your Supabase dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def drop_old_foreign_keys():
    """Drop foreign key constraints from old listings table if they exist"""
    try:
        supabase = SupabaseManager()
        
        print("🗑️  Dropping foreign key constraints from old listings table...")
        
        # SQL to drop foreign key constraints
        drop_fk_sql = """
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
            END LOOP;
        END $$;
        """
        
        try:
            response = supabase.client.postgrest.rpc('exec_sql', {'sql': drop_fk_sql}).execute()
            print("✅ Old foreign key constraints dropped")
        except Exception as e:
            print(f"⚠️  Could not drop old foreign keys: {str(e)}")
            print("   This is normal if no foreign keys exist")
            
    except Exception as e:
        print(f"❌ Error dropping foreign keys: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "drop-fk":
        drop_old_foreign_keys()
    else:
        create_listings_v2_table_with_fk()
