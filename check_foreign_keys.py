#!/usr/bin/env python3
"""
Check foreign key relationships in the database
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.supabase_manager import SupabaseManager

def check_foreign_keys():
    """Check all foreign key relationships in the database"""
    try:
        supabase = SupabaseManager()
        
        print("🔍 Checking foreign key relationships...")
        print("=" * 50)
        
        # SQL to get all foreign key relationships
        fk_query = """
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
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
        ORDER BY tc.table_name, kcu.column_name;
        """
        
        try:
            result = supabase.client.postgrest.rpc('exec_sql', {'sql': fk_query}).execute()
            
            if result.data:
                print("📋 Current Foreign Key Relationships:")
                print("-" * 50)
                
                current_table = None
                for fk in result.data:
                    table_name = fk['table_name']
                    if table_name != current_table:
                        current_table = table_name
                        print(f"\n📊 Table: {table_name}")
                    
                    print(f"   🔗 {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                    print(f"      Constraint: {fk['constraint_name']}")
                
                # Check specific relationships
                print(f"\n🔍 Specific Checks:")
                print("-" * 30)
                
                # Check if listings table has foreign keys
                listings_fks = [fk for fk in result.data if fk['table_name'] == 'listings']
                if listings_fks:
                    print("✅ listings table has foreign key relationships:")
                    for fk in listings_fks:
                        print(f"   - {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                else:
                    print("ℹ️  listings table has no foreign key relationships")
                
                # Check if listings_v2 table has foreign keys
                listings_v2_fks = [fk for fk in result.data if fk['table_name'] == 'listings_v2']
                if listings_v2_fks:
                    print("✅ listings_v2 table has foreign key relationships:")
                    for fk in listings_v2_fks:
                        print(f"   - {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                else:
                    print("⚠️  listings_v2 table has no foreign key relationships")
                
                # Check profiles table relationships
                profiles_referenced = [fk for fk in result.data if fk['foreign_table_name'] == 'profiles']
                if profiles_referenced:
                    print("✅ profiles table is referenced by:")
                    for fk in profiles_referenced:
                        print(f"   - {fk['table_name']}.{fk['column_name']}")
                else:
                    print("ℹ️  profiles table is not referenced by any foreign keys")
                
            else:
                print("ℹ️  No foreign key relationships found in the database")
                
        except Exception as e:
            print(f"❌ Error checking foreign keys: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def add_foreign_key_to_listings_v2():
    """Add foreign key constraint to listings_v2 table if it doesn't exist"""
    try:
        supabase = SupabaseManager()
        
        print("🔗 Adding foreign key constraint to listings_v2...")
        
        # SQL to add foreign key constraint
        add_fk_sql = """
        ALTER TABLE listings_v2 
        ADD CONSTRAINT fk_listings_v2_host_id 
        FOREIGN KEY (host_id) 
        REFERENCES profiles(id) 
        ON DELETE CASCADE;
        """
        
        try:
            response = supabase.client.postgrest.rpc('exec_sql', {'sql': add_fk_sql}).execute()
            print("✅ Foreign key constraint added to listings_v2")
            return True
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️  Foreign key constraint already exists")
                return True
            else:
                print(f"❌ Error adding foreign key constraint: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def remove_foreign_key_from_listings():
    """Remove foreign key constraints from old listings table"""
    try:
        supabase = SupabaseManager()
        
        print("🗑️  Removing foreign key constraints from listings table...")
        
        # SQL to remove foreign key constraints
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
            print("✅ Foreign key constraints removed from listings table")
            return True
        except Exception as e:
            print(f"⚠️  Could not remove foreign key constraints: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "add-fk":
            success = add_foreign_key_to_listings_v2()
        elif command == "remove-fk":
            success = remove_foreign_key_from_listings()
        elif command == "help":
            print("Usage:")
            print("  python check_foreign_keys.py          # Check all foreign keys")
            print("  python check_foreign_keys.py add-fk   # Add FK to listings_v2")
            print("  python check_foreign_keys.py remove-fk # Remove FK from listings")
            print("  python check_foreign_keys.py help     # Show this help")
            success = True
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python check_foreign_keys.py help' for usage information")
            success = False
    else:
        success = check_foreign_keys()
    
    sys.exit(0 if success else 1)
