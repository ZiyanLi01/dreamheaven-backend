from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager

router = APIRouter()

# Initialize Supabase client with error handling
try:
    supabase = SupabaseManager()
    print("✅ Supabase client initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Supabase client: {str(e)}")
    supabase = None

# Pydantic models
class ListingBase(BaseModel):
    title: str
    description: str
    property_type: str
    bedrooms: int
    bathrooms: int
    max_guests: int
    square_feet: int
    price_per_night: float
    price_per_month: float
    city: str
    state: str
    country: str
    latitude: float
    longitude: float
    address: str
    neighborhood: str
    amenities: List[str]
    images: List[str]
    is_available: bool = True
    is_featured: bool = False

class ListingCreate(ListingBase):
    host_id: str

class ListingResponse(ListingBase):
    id: str
    host_id: str
    rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    max_guests: Optional[int] = None
    square_feet: Optional[int] = None
    price_per_night: Optional[float] = None
    price_per_month: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    is_available: Optional[bool] = None
    is_featured: Optional[bool] = None

# Pydantic models for the new endpoint
class ListingItem(BaseModel):
    id: str
    status: str
    address: str
    location: str
    sqft: int
    garages: int
    bedrooms: int
    bathrooms: int
    agent: str
    listingAge: str
    price: float
    imageUrl: str
    # New fields for enhanced schema
    listing_type: str  # rent, sale, or both
    price_for_sale: Optional[float] = None
    price_per_month: Optional[float] = None
    has_yard: bool = False
    has_parking_lot: bool = False

class PaginatedListingsResponse(BaseModel):
    results: dict  # Changed from List[ListingItem] to dict with UUID keys
    page: int
    limit: int
    total: int
    has_more: bool

@router.get("/", response_model=PaginatedListingsResponse)
async def get_filtered_listings(
    location: Optional[str] = Query(None, description="Filter by location (e.g., 'Los Angeles, CA')"),
    bed: Optional[str] = Query(None, description="Filter by bedrooms ('Any', '2+', or specific number)"),
    bath: Optional[str] = Query(None, description="Filter by bathrooms ('Any', '2+', or specific number)"),
    rent: Optional[str] = Query(None, description="Filter by rent type ('For Rent' or 'For Sale')"),
    sortBy: Optional[str] = Query(None, description="Sort by field (e.g., 'price', 'bedrooms')"),
    sortOrder: Optional[str] = Query("asc", description="Sort order ('asc' or 'desc')"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(30, ge=1, le=100, description="Number of records per page")
):
    """Get filtered property listings with pagination support"""
    try:
        # Check if Supabase client is available
        if supabase is None:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Build query with ALL fields from the listings table
        try:
            query = supabase.client.table("listings").select("*")
            print(f"✅ Query built successfully with filters: location={location}, bed={bed}, bath={bath}, rent={rent}, sortBy={sortBy}, sortOrder={sortOrder}")
        except Exception as e:
            print(f"❌ Error building query: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error building database query: {str(e)}")
        
        # Apply location filter
        if location:
            # Split location into city and state (e.g., "Los Angeles, CA")
            location_parts = location.split(',')
            if len(location_parts) == 2:
                city = location_parts[0].strip()
                state = location_parts[1].strip()
                query = query.eq("city", city).eq("state", state)
            else:
                # Fallback to just city if no comma found
                query = query.eq("city", location.strip())
        
        # Apply bedrooms filter
        if bed and bed != "Any":
            if bed == "2+":
                query = query.gte("bedrooms", 2)
            else:
                try:
                    bed_count = int(bed)
                    query = query.eq("bedrooms", bed_count)
                except ValueError:
                    # If parsing fails, skip this filter
                    pass
        
        # Apply bathrooms filter
        if bath and bath != "Any":
            if bath == "2+":
                query = query.gte("bathrooms", 2)
            else:
                try:
                    bath_count = int(bath)
                    query = query.eq("bathrooms", bath_count)
                except ValueError:
                    # If parsing fails, skip this filter
                    pass
        
        # Apply rent filter
        if rent:
            if rent == "For Rent":
                # Filter for properties with property_listing_type = 'rent' or 'both'
                query = query.in_("property_listing_type", ["rent", "both"])
            elif rent == "For Sale":
                # Filter for properties with property_listing_type = 'sale' or 'both'
                query = query.in_("property_listing_type", ["sale", "both"])
        
        # Apply sorting
        if sortBy:
            # Map frontend sort fields to database fields
            sort_field_mapping = {
                "price": "price_per_night",  # Default to nightly price for sorting
                "bedrooms": "bedrooms",
                "bathrooms": "bathrooms",
                "square_feet": "square_feet"
            }
            
            db_sort_field = sort_field_mapping.get(sortBy, "price_per_night")
            sort_direction = "asc" if sortOrder and sortOrder.lower() == "asc" else "desc"
            
            if sort_direction == "asc":
                query = query.order(db_sort_field, desc=False)
            else:
                query = query.order(db_sort_field, desc=True)
        
        # Get total count first
        try:
            count_query = query
            count_result = count_query.execute()
            total = len(count_result.data) if count_result.data else 0
            print(f"✅ Count query executed successfully: {total} total results")
        except Exception as e:
            print(f"❌ Error executing count query: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error counting results: {str(e)}")
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        try:
            result = query.execute()
            print(f"✅ Main query executed successfully: {len(result.data) if result.data else 0} results returned")
        except Exception as e:
            print(f"❌ Error executing main query: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")
        
        if result.data:
            # Transform data to return full listing objects
            listings_dict = {}
            for item in result.data:
                # Return the full listing object as-is from the database
                # This includes all fields: id, title, description, property_type, property_listing_type,
                # bedrooms, bathrooms, square_feet, garage_number, price_per_night, price_per_month, price_for_sale,
                # city, state, country, latitude, longitude, address, neighborhood,
                # has_yard, has_parking_lot, amenities, images, is_available, is_featured, rating, review_count
                
                # Use the listing ID as the key in the dictionary
                listings_dict[item.get("id", "")] = item
            
            # Calculate if there are more pages
            has_more = (page * limit) < total
            
            return PaginatedListingsResponse(
                results=listings_dict,
                page=page,
                limit=limit,
                total=total,
                has_more=has_more
            )
        else:
            return PaginatedListingsResponse(
                results={},
                page=page,
                limit=limit,
                total=0,
                has_more=False
            )
            
    except Exception as e:
        # Log the error for debugging
        print(f"❌ Error in get_filtered_listings: {str(e)}")
        # Return 500 error with detailed message
        raise HTTPException(status_code=500, detail=f"Error fetching listings: {str(e)}")

@router.get("/{listing_id}")
async def get_listing(listing_id: str):
    """Get a specific listing by ID - returns full listing object with all fields"""
    try:
        if supabase is None:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        result = supabase.client.table("listings").select("*").eq("id", listing_id).execute()
        
        if result.data:
            # Return the full listing object as-is from the database
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Listing not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_listing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching listing: {str(e)}")

@router.post("/", response_model=ListingResponse)
async def create_listing(listing: ListingCreate):
    """Create a new listing"""
    try:
        listing_data = listing.dict()
        listing_data["created_at"] = datetime.now().isoformat()
        listing_data["updated_at"] = datetime.now().isoformat()
        listing_data["rating"] = 0.0
        listing_data["review_count"] = 0
        
        result = supabase.client.table("listings").insert(listing_data).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=400, detail="Failed to create listing")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating listing: {str(e)}")

@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(listing_id: str, listing: ListingUpdate):
    """Update an existing listing"""
    try:
        update_data = listing.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()
        
        result = supabase.client.table("listings").update(update_data).eq("id", listing_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Listing not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating listing: {str(e)}")

@router.delete("/{listing_id}")
async def delete_listing(listing_id: str):
    """Delete a listing"""
    try:
        result = supabase.client.table("listings").delete().eq("id", listing_id).execute()
        
        if result.data:
            return {"message": "Listing deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Listing not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting listing: {str(e)}")

@router.get("/host/{host_id}", response_model=List[ListingResponse])
async def get_listings_by_host(host_id: str):
    """Get all listings for a specific host"""
    try:
        result = supabase.client.table("listings").select("*").eq("host_id", host_id).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching host listings: {str(e)}")

@router.get("/cities/list")
async def get_cities():
    """Get list of all cities with listings"""
    try:
        result = supabase.client.table("listings").select("city, state").execute()
        
        if result.data:
            # Get unique cities
            cities = set()
            for item in result.data:
                cities.add(f"{item['city']}, {item['state']}")
            
            return sorted(list(cities))
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cities: {str(e)}")

@router.get("/types/list")
async def get_property_types():
    """Get list of all property types"""
    try:
        result = supabase.client.table("listings").select("property_type").execute()
        
        if result.data:
            # Get unique property types
            types = set()
            for item in result.data:
                types.add(item['property_type'])
            
            return sorted(list(types))
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching property types: {str(e)}") 