# Listings V2 Migration Guide

This guide explains how to migrate from the old `listings` table to the new `listings_v2` table with enhanced schema.

## Overview

The `listings_v2` table provides an enhanced schema with additional fields for better property management and AI/ML capabilities:

### New Features in listings_v2:
- **Enhanced Property Details**: Additional fields like `floor`, `year_built`, `year_renovated`, `school_rating`, `crime_index`, etc.
- **AI/ML Ready**: `embedding_text` field for vector search and AI-powered features
- **Better Pricing Structure**: Separate fields for `price_per_month` and `price_for_sale`
- **Property Features**: `has_yard`, `has_parking_lot`, `garage_number`
- **Tags System**: `tags` field for categorization
- **Location Indices**: `shopping_idx`, `grocery_idx` for proximity metrics

## Migration Steps

### 1. Create the listings_v2 Table with Foreign Keys

First, ensure the `listings_v2` table exists in your Supabase database with proper foreign key constraints:

```bash
# Create table with foreign key constraints
python create_listings_v2_with_fk.py

# Or check current foreign key relationships
python check_foreign_keys.py
```

### 2. Set Up Foreign Key Relationships

Ensure the foreign key relationships are properly set up:

```bash
# Check current foreign key relationships
python check_foreign_keys.py

# Add foreign key constraint to listings_v2 if needed
python check_foreign_keys.py add-fk

# Remove foreign key constraints from old listings table (optional)
python check_foreign_keys.py remove-fk
```

### 3. Test the Migration

Run the test script to verify everything is working:

```bash
python test_listings_v2_migration.py
```

### 4. Migrate Existing Data (Optional)

If you have existing data in the old `listings` table, migrate it:

```bash
python migrate_to_listings_v2.py
```

To verify the migration:
```bash
python migrate_to_listings_v2.py verify
```

### 5. Generate New Data

Generate new data using the enhanced schema:

```bash
python scripts/generate_data.py
```

## Schema Comparison

### Old listings table:
```sql
- id, host_id, title, description, property_type
- bedrooms, bathrooms, max_guests, square_feet
- price_per_night, price_per_month, price_for_sale
- city, state, country, latitude, longitude, address, neighborhood
- amenities, images, is_available, is_featured
- rating, review_count, created_at, updated_at
```

### New listings_v2 table:
```sql
- id, host_id, title, description, property_type, property_listing_type
- bedrooms, bathrooms, square_feet
- price_per_month, price_for_sale
- city, state, country, latitude, longitude, address, neighborhood
- garage_number, has_yard, has_parking_lot
- amenities, images, is_available, is_featured
- rating, review_count
- floor, year_built, year_renovated, school_rating, crime_index
- facing, shopping_idx, grocery_idx, tags
- embedding_text, embedding
- created_at, updated_at
```

## Database Schema Changes

### Foreign Key Relationships

The `listings_v2` table now has proper foreign key constraints:

- `host_id` references `profiles(id)` with CASCADE DELETE
- This ensures data integrity and proper cleanup when hosts are deleted

### API Changes

The API has been updated to use the `listings_v2` table:

- All endpoints now query `listings_v2` instead of `listings`
- Pydantic models updated to match new schema
- Price sorting now uses `price_per_month` instead of `price_per_night`
- New fields available in API responses

## Benefits

1. **Better Data Structure**: More comprehensive property information
2. **AI/ML Ready**: Built-in support for vector embeddings and AI features
3. **Enhanced Search**: Better filtering and search capabilities
4. **Future-Proof**: Designed for advanced features like RAG search

## Rollback Plan

If you need to rollback to the old table:

1. Update the API routes to use `listings` instead of `listings_v2`
2. Update the SupabaseManager to use the old table
3. Update Pydantic models to match old schema

## Support

If you encounter any issues during migration:

1. Check the test script output for specific errors
2. Verify your Supabase connection and permissions
3. Ensure the `listings_v2` table was created successfully
4. Check the migration logs for detailed error messages
