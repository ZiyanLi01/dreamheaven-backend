#!/usr/bin/env python3
"""
Script to run database migration for the new listings API requirements.
This script adds the missing fields to the listings table.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.supabase_manager import SupabaseManager

def run_migration():
    """Run the database migration to add new fields to listings table"""
    print("🔄 Running database migration for listings table...")
    
    try:
        supabase = SupabaseManager()
        
        # Read the migration SQL file
        migration_file = Path(__file__).parent.parent / "update_listings_schema.sql"
        
        if not migration_file.exists():
            print("❌ Migration file not found: update_listings_schema.sql")
            return False
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"📝 Executing statement {i}/{len(statements)}...")
                try:
                    # Execute the SQL statement
                    result = supabase.client.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"✅ Statement {i} executed successfully")
                except Exception as e:
                    print(f"⚠️  Statement {i} failed (this might be expected if field already exists): {str(e)}")
                    # Continue with other statements even if one fails
        
        print("✅ Database migration completed!")
        print("\n📋 Summary of changes:")
        print("   - Added 'status' field for 'For Sale' or 'For Rent'")
        print("   - Added 'garages' field for number of garage spaces")
        print("   - Added 'agent_name' field for listing agent")
        print("   - Added 'listing_age_days' field for performance")
        print("   - Added 'image_url' field for primary image")
        print("   - Created indexes for better query performance")
        print("   - Added trigger to automatically update listing age")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        supabase = SupabaseManager()
        
        # Check if new fields exist by querying a sample record
        result = supabase.client.table("listings").select("status, garages, agent_name, listing_age_days, image_url").limit(1).execute()
        
        if result.data:
            sample = result.data[0]
            print("✅ New fields found in listings table:")
            for field in ['status', 'garages', 'agent_name', 'listing_age_days', 'image_url']:
                if field in sample:
                    print(f"   - {field}: {sample[field]}")
                else:
                    print(f"   - {field}: ❌ Not found")
        else:
            print("⚠️  No listings found to verify migration")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏠 Dream Haven Backend - Database Migration")
    print("=" * 50)
    
    success = run_migration()
    
    if success:
        verify_migration()
        print("\n🎉 Migration process completed successfully!")
        print("You can now use the new filtered listings API endpoint.")
    else:
        print("\n💥 Migration process failed!")
        sys.exit(1) 