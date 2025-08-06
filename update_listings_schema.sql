-- Migration script to update listings table for new API requirements
-- Add missing fields to support the new filtered listings endpoint

-- Add status field for "For Sale" or "For Rent"
ALTER TABLE listings ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'For Sale';

-- Add garages field
ALTER TABLE listings ADD COLUMN IF NOT EXISTS garages INTEGER DEFAULT 1;

-- Add agent field (could reference profiles table)
ALTER TABLE listings ADD COLUMN IF NOT EXISTS agent_name TEXT;

-- Add listing_age field (computed field, but we can store it for performance)
ALTER TABLE listings ADD COLUMN IF NOT EXISTS listing_age_days INTEGER DEFAULT 0;

-- Add image_url field (first image from images array)
ALTER TABLE listings ADD COLUMN IF NOT EXISTS image_url TEXT;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
CREATE INDEX IF NOT EXISTS idx_listings_location ON listings(city, state);
CREATE INDEX IF NOT EXISTS idx_listings_bedrooms ON listings(bedrooms);
CREATE INDEX IF NOT EXISTS idx_listings_bathrooms ON listings(bathrooms);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price_per_night);

-- Update existing records to set status based on property_type
UPDATE listings 
SET status = CASE 
    WHEN property_type IN ('Apartment', 'Studio') THEN 'For Rent'
    ELSE 'For Sale'
END
WHERE status IS NULL;

-- Update existing records to set image_url from images array
UPDATE listings 
SET image_url = images[1]
WHERE image_url IS NULL AND array_length(images, 1) > 0;

-- Update existing records to calculate listing_age_days
UPDATE listings 
SET listing_age_days = EXTRACT(DAY FROM (NOW() - created_at))
WHERE listing_age_days = 0;

-- Add a function to automatically update listing_age_days
CREATE OR REPLACE FUNCTION update_listing_age()
RETURNS TRIGGER AS $$
BEGIN
    NEW.listing_age_days = EXTRACT(DAY FROM (NOW() - NEW.created_at));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update listing_age_days
DROP TRIGGER IF EXISTS trigger_update_listing_age ON listings;
CREATE TRIGGER trigger_update_listing_age
    BEFORE UPDATE ON listings
    FOR EACH ROW
    EXECUTE FUNCTION update_listing_age();

-- Add comments for documentation
COMMENT ON COLUMN listings.status IS 'Property status: For Sale or For Rent';
COMMENT ON COLUMN listings.garages IS 'Number of garage spaces';
COMMENT ON COLUMN listings.agent_name IS 'Name of the listing agent';
COMMENT ON COLUMN listings.listing_age_days IS 'Number of days since listing was created';
COMMENT ON COLUMN listings.image_url IS 'Primary image URL for the listing'; 