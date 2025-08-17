#!/usr/bin/env python3
"""
Create listings_v2 table with the new schema
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager

def create_listings_v2_table():
    """Create the listings_v2 table"""
    try:
        supabase = SupabaseManager()
        
        print("🚀 Creating listings_v2 table...")
        
        # Create facing enum
        try:
            supabase.client.rpc('exec_sql', {
                'sql': "DO $$ BEGIN CREATE TYPE facing_direction AS ENUM ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'); EXCEPTION WHEN duplicate_object THEN null; END $$;"
            }).execute()
            print("✅ Facing enum created")
        except Exception as e:
            print(f"⚠️  Facing enum creation: {str(e)}")
        
        # Enable pgvector
        try:
            supabase.client.rpc('exec_sql', {
                'sql': "CREATE EXTENSION IF NOT EXISTS vector;"
            }).execute()
            print("✅ pgvector extension enabled")
        except Exception as e:
            print(f"⚠️  pgvector extension: {str(e)}")
        
        # Create the table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS listings_v2 (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            host_id UUID NOT NULL,
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
        
        try:
            supabase.client.rpc('exec_sql', {'sql': create_table_sql}).execute()
            print("✅ listings_v2 table created")
        except Exception as e:
            print(f"❌ Error creating table: {str(e)}")
            return False
        
        # Verify the table was created
        try:
            result = supabase.client.table("listings_v2").select("*").limit(1).execute()
            print("✅ listings_v2 table verified - exists and accessible")
            return True
        except Exception as e:
            print(f"❌ Error verifying table: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    create_listings_v2_table()
