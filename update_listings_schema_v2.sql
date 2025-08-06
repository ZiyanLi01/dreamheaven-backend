-- Migration script to update listings table for enhanced property management
-- Version 2: Add type, dual pricing, garage details, yard, and parking

-- Add property type field (rent/sale/both)
ALTER TABLE listings ADD COLUMN IF NOT EXISTS property_listing_type TEXT DEFAULT 'sale';

-- Add price fields for different listing types
ALTER TABLE listings ADD COLUMN IF NOT EXISTS price_for_sale DECIMAL(12,2);
ALTER TABLE listings ADD COLUMN IF NOT EXISTS price_per_month DECIMAL(10,2);

-- Add garage and parking details
ALTER TABLE listings ADD COLUMN IF NOT EXISTS garage_number INTEGER DEFAULT 0;
ALTER TABLE listings ADD COLUMN IF NOT EXISTS has_yard BOOLEAN DEFAULT FALSE;
ALTER TABLE listings ADD COLUMN IF NOT EXISTS has_parking_lot BOOLEAN DEFAULT FALSE;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_listings_type ON listings(property_listing_type);
CREATE INDEX IF NOT EXISTS idx_listings_price_sale ON listings(price_for_sale);
CREATE INDEX IF NOT EXISTS idx_listings_price_rent ON listings(price_per_month);
CREATE INDEX IF NOT EXISTS idx_listings_garage ON listings(garage_number);
CREATE INDEX IF NOT EXISTS idx_listings_yard ON listings(has_yard);
CREATE INDEX IF NOT EXISTS idx_listings_parking ON listings(has_parking_lot);

-- Update existing records to set appropriate values based on current data
-- Map existing property_type to new property_listing_type
UPDATE listings 
SET property_listing_type = CASE 
    WHEN property_type IN ('Apartment', 'Studio') THEN 'rent'
    WHEN property_type IN ('House', 'Condo', 'Townhouse', 'Villa', 'Penthouse', 'Duplex', 'Cottage') THEN 'sale'
    ELSE 'sale'
END
WHERE property_listing_type IS NULL;

-- Set price_for_sale for sale properties (using existing price_per_night as base)
UPDATE listings 
SET price_for_sale = price_per_night * 30 * 12  -- Convert nightly rate to annual sale price
WHERE property_listing_type = 'sale' AND price_for_sale IS NULL;

-- Set price_per_month for rent properties (using existing price_per_night as base)
UPDATE listings 
SET price_per_month = price_per_night * 30  -- Convert nightly rate to monthly rent
WHERE property_listing_type = 'rent' AND price_per_month IS NULL;

-- Set some properties as both rent and sale (mixed use)
UPDATE listings 
SET property_listing_type = 'both',
    price_for_sale = price_per_night * 30 * 12,
    price_per_month = price_per_night * 30
WHERE id IN (
    SELECT id FROM listings 
    WHERE property_type IN ('House', 'Condo', 'Townhouse') 
    AND random() < 0.1  -- 10% of these properties will be both
    LIMIT 50
);

-- Set garage numbers based on property type and size
UPDATE listings 
SET garage_number = CASE 
    WHEN property_type IN ('House', 'Villa') THEN 
        CASE 
            WHEN square_feet > 2000 THEN 2
            ELSE 1
        END
    WHEN property_type IN ('Condo', 'Townhouse') THEN 1
    ELSE 0
    END
WHERE garage_number = 0;

-- Set yard availability
UPDATE listings 
SET has_yard = CASE 
    WHEN property_type IN ('House', 'Villa', 'Cottage') THEN TRUE
    WHEN property_type IN ('Townhouse') AND random() < 0.7 THEN TRUE
    ELSE FALSE
    END
WHERE has_yard IS NULL;

-- Set parking lot availability
UPDATE listings 
SET has_parking_lot = CASE 
    WHEN property_type IN ('Apartment', 'Condo', 'Studio') THEN TRUE
    WHEN property_type IN ('House', 'Villa') AND random() < 0.3 THEN TRUE
    ELSE FALSE
    END
WHERE has_parking_lot IS NULL;

-- Add constraints to ensure data integrity
ALTER TABLE listings ADD CONSTRAINT IF NOT EXISTS check_listing_type 
    CHECK (property_listing_type IN ('rent', 'sale', 'both'));

ALTER TABLE listings ADD CONSTRAINT IF NOT EXISTS check_price_sale 
    CHECK (price_for_sale IS NULL OR price_for_sale > 0);

ALTER TABLE listings ADD CONSTRAINT IF NOT EXISTS check_price_rent 
    CHECK (price_per_month IS NULL OR price_per_month > 0);

ALTER TABLE listings ADD CONSTRAINT IF NOT EXISTS check_garage_number 
    CHECK (garage_number >= 0);

-- Add comments for documentation
COMMENT ON COLUMN listings.property_listing_type IS 'Property listing type: rent, sale, or both';
COMMENT ON COLUMN listings.price_for_sale IS 'Sale price for the property (NULL if not for sale)';
COMMENT ON COLUMN listings.price_per_month IS 'Monthly rent price (NULL if not for rent)';
COMMENT ON COLUMN listings.garage_number IS 'Number of garage spaces available';
COMMENT ON COLUMN listings.has_yard IS 'Whether the property has a yard/garden';
COMMENT ON COLUMN listings.has_parking_lot IS 'Whether the property has a parking lot';

-- Create a view for easier querying of properties by type
CREATE OR REPLACE VIEW properties_for_sale AS
SELECT * FROM listings 
WHERE property_listing_type IN ('sale', 'both') 
AND price_for_sale IS NOT NULL;

CREATE OR REPLACE VIEW properties_for_rent AS
SELECT * FROM listings 
WHERE property_listing_type IN ('rent', 'both') 
AND price_per_month IS NOT NULL;

-- Create a function to get property pricing info
CREATE OR REPLACE FUNCTION get_property_pricing(listing_id UUID)
RETURNS TABLE(
    listing_type TEXT,
    sale_price DECIMAL(12,2),
    monthly_rent DECIMAL(10,2),
    has_dual_pricing BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.property_listing_type,
        l.price_for_sale,
        l.price_per_month,
        l.property_listing_type = 'both'
    FROM listings l
    WHERE l.id = listing_id;
END;
$$ LANGUAGE plpgsql; 