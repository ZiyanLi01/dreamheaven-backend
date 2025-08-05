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

@router.get("/", response_model=List[ListingResponse])
async def get_listings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    city: Optional[str] = Query(None, description="Filter by city"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price per night"),
    min_bedrooms: Optional[int] = Query(None, ge=0, description="Minimum number of bedrooms"),
    max_bedrooms: Optional[int] = Query(None, ge=0, description="Maximum number of bedrooms"),
    available_only: bool = Query(True, description="Show only available listings"),
    featured_only: bool = Query(False, description="Show only featured listings")
):
    """Get all listings with optional filters"""
    try:
        query = supabase.client.table("listings").select("*")
        
        # Apply filters
        if city:
            query = query.eq("city", city)
        if property_type:
            query = query.eq("property_type", property_type)
        if min_price is not None:
            query = query.gte("price_per_night", min_price)
        if max_price is not None:
            query = query.lte("price_per_night", max_price)
        if min_bedrooms is not None:
            query = query.gte("bedrooms", min_bedrooms)
        if max_bedrooms is not None:
            query = query.lte("bedrooms", max_bedrooms)
        if available_only:
            query = query.eq("is_available", True)
        if featured_only:
            query = query.eq("is_featured", True)
        
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        result = query.execute()
        
        if result.data:
            return result.data
        else:
            return []
            
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