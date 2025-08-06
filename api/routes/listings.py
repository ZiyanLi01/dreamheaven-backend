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
supabase = SupabaseManager()

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

class PaginatedListingsResponse(BaseModel):
    results: List[ListingItem]
    page: int
    limit: int
    total: int
    has_more: bool

@router.get("/", response_model=PaginatedListingsResponse)
async def get_filtered_listings(
    location: Optional[str] = Query(None, description="Filter by location (city)"),
    bedrooms: Optional[int] = Query(None, ge=0, description="Filter by number of bedrooms"),
    bathrooms: Optional[int] = Query(None, ge=0, description="Filter by number of bathrooms"),
    status: Optional[str] = Query(None, description="Filter by status (For Sale or For Rent)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(30, ge=1, le=100, description="Number of records per page")
):
    """Get filtered property listings with pagination support"""
    try:
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Build query
        query = supabase.client.table("listings").select("*")
        
        # Apply filters
        if location:
            query = query.eq("city", location)
        if bedrooms is not None:
            query = query.eq("bedrooms", bedrooms)
        if bathrooms is not None:
            query = query.eq("bathrooms", bathrooms)
        if status:
            # Map status to property_type since status field doesn't exist yet
            if status.lower() == "for sale":
                query = query.eq("property_type", "House")  # Assuming houses are for sale
            elif status.lower() == "for rent":
                query = query.eq("property_type", "Apartment")  # Assuming apartments are for rent
        
        # Get total count first
        count_query = query
        count_result = count_query.execute()
        total = len(count_result.data) if count_result.data else 0
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        result = query.execute()
        
        if result.data:
            # Transform data to match required response format
            listings = []
            for item in result.data:
                # Get listing age (use stored value if available, otherwise calculate)
                listing_age_days = item.get("listing_age_days")
                if listing_age_days is not None:
                    listing_age_str = f"{listing_age_days} days ago" if listing_age_days > 0 else "Today"
                else:
                    try:
                        created_date = datetime.fromisoformat(item.get("created_at", datetime.now().isoformat()))
                        # Handle timezone-aware datetime
                        if created_date.tzinfo is None:
                            created_date = created_date.replace(tzinfo=None)
                        current_time = datetime.now().replace(tzinfo=None)
                        listing_age = (current_time - created_date).days
                        listing_age_str = f"{listing_age} days ago" if listing_age > 0 else "Today"
                    except Exception:
                        listing_age_str = "Recently"
                
                # Get image URL (use stored value if available, otherwise get from images array)
                image_url = item.get("image_url")
                if not image_url:
                    image_url = item.get("images", [""])[0] if item.get("images") else ""
                
                # Get status (use stored value if available, otherwise map from property_type)
                listing_status = item.get("status")
                if not listing_status:
                    status_mapping = {
                        "House": "For Sale",
                        "Apartment": "For Rent",
                        "Condo": "For Sale",
                        "Townhouse": "For Sale"
                    }
                    listing_status = status_mapping.get(item.get("property_type", "House"), "For Sale")
                
                # Create location string
                location_str = f"{item.get('city', '')}, {item.get('state', '')}"
                
                # Get agent name (use stored value if available, otherwise generate from host_id)
                agent_name = item.get("agent_name")
                if not agent_name:
                    agent_name = f"Agent {item.get('host_id', '')[:8]}"
                
                listing_item = ListingItem(
                    id=item.get("id", ""),
                    status=listing_status,
                    address=item.get("address", ""),
                    location=location_str,
                    sqft=item.get("square_feet", 0),
                    garages=item.get("garages", 1),  # Use stored value or default
                    bedrooms=item.get("bedrooms", 0),
                    bathrooms=item.get("bathrooms", 0),
                    agent=agent_name,
                    listingAge=listing_age_str,
                    price=float(item.get("price_per_night", 0)),
                    imageUrl=image_url
                )
                listings.append(listing_item)
            
            # Calculate if there are more pages
            has_more = (page * limit) < total
            
            return PaginatedListingsResponse(
                results=listings,
                page=page,
                limit=limit,
                total=total,
                has_more=has_more
            )
        else:
            return PaginatedListingsResponse(
                results=[],
                page=page,
                limit=limit,
                total=0,
                has_more=False
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching listings: {str(e)}")

@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: str):
    """Get a specific listing by ID"""
    try:
        result = supabase.client.table("listings").select("*").eq("id", listing_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Listing not found")
            
    except HTTPException:
        raise
    except Exception as e:
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