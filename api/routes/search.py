from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager

router = APIRouter()
supabase = SupabaseManager()

# Pydantic models
class SearchResult(BaseModel):
    id: str
    title: str
    description: str
    property_type: str
    bedrooms: int
    bathrooms: int
    price_per_night: float
    city: str
    state: str
    neighborhood: str
    amenities: List[str]
    images: List[str]
    rating: float
    review_count: int
    is_available: bool
    is_featured: bool
    latitude: float
    longitude: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    page: int
    limit: int
    has_more: bool

@router.get("/", response_model=SearchResponse)
async def search_listings(
    q: Optional[str] = Query(None, description="Search query"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price per night"),
    min_bedrooms: Optional[int] = Query(None, ge=0, description="Minimum number of bedrooms"),
    max_bedrooms: Optional[int] = Query(None, ge=0, description="Maximum number of bedrooms"),
    min_bathrooms: Optional[int] = Query(None, ge=0, description="Minimum number of bathrooms"),
    amenities: Optional[str] = Query(None, description="Comma-separated list of amenities"),
    available_only: bool = Query(True, description="Show only available listings"),
    featured_only: bool = Query(False, description="Show only featured listings"),
    sort_by: str = Query("created_at", description="Sort by field (price_per_night, rating, created_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page")
):
    """Search listings with various filters and sorting options"""
    try:
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Build query
        query = supabase.client.table("listings").select("*")
        
        # Apply text search if query provided
        if q:
            # Search in title, description, city, neighborhood
            query = query.or_(f"title.ilike.%{q}%,description.ilike.%{q}%,city.ilike.%{q}%,neighborhood.ilike.%{q}%")
        
        # Apply filters
        if city:
            query = query.eq("city", city)
        if state:
            query = query.eq("state", state)
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
        if min_bathrooms is not None:
            query = query.gte("bathrooms", min_bathrooms)
        if available_only:
            query = query.eq("is_available", True)
        if featured_only:
            query = query.eq("is_featured", True)
        
        # Apply sorting
        if sort_order.lower() == "asc":
            query = query.order(sort_by, desc=False)
        else:
            query = query.order(sort_by, desc=True)
        
        # Get total count first
        count_query = query
        count_result = count_query.execute()
        total = len(count_result.data) if count_result.data else 0
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        result = query.execute()
        
        listings = result.data if result.data else []
        
        # Filter by amenities if specified
        if amenities:
            amenity_list = [a.strip() for a in amenities.split(",")]
            filtered_listings = []
            for listing in listings:
                if listing.get("amenities"):
                    listing_amenities = listing["amenities"]
                    if any(amenity in listing_amenities for amenity in amenity_list):
                        filtered_listings.append(listing)
            listings = filtered_listings
        
        # Calculate if there are more results
        has_more = (offset + limit) < total
        
        return SearchResponse(
            results=listings,
            total=total,
            page=page,
            limit=limit,
            has_more=has_more
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/nearby", response_model=List[SearchResult])
async def search_nearby(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius_km: float = Query(10.0, ge=0.1, le=100.0, description="Search radius in kilometers"),
    limit: int = Query(20, ge=1, le=100, description="Number of results")
):
    """Search for listings near a specific location"""
    try:
        # Convert radius from km to degrees (approximate)
        # 1 degree ≈ 111 km
        radius_degrees = radius_km / 111.0
        
        # Calculate bounding box
        lat_min = latitude - radius_degrees
        lat_max = latitude + radius_degrees
        lng_min = longitude - radius_degrees
        lng_max = longitude + radius_degrees
        
        # Query listings within bounding box
        query = supabase.client.table("listings").select("*").eq("is_available", True)
        query = query.gte("latitude", lat_min).lte("latitude", lat_max)
        query = query.gte("longitude", lng_min).lte("longitude", lng_max)
        query = query.limit(limit)
        
        result = query.execute()
        
        listings = result.data if result.data else []
        
        # Sort by distance (simple calculation)
        def calculate_distance(lat1, lng1, lat2, lng2):
            return ((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) ** 0.5
        
        listings.sort(key=lambda x: calculate_distance(
            latitude, longitude, x["latitude"], x["longitude"]
        ))
        
        return listings[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nearby search failed: {str(e)}")

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Search query for suggestions")
):
    """Get search suggestions based on partial query"""
    try:
        suggestions = {
            "cities": [],
            "neighborhoods": [],
            "property_types": [],
            "amenities": []
        }
        
        # Get city suggestions
        city_result = supabase.client.table("listings").select("city").ilike("city", f"%{q}%").limit(5).execute()
        if city_result.data:
            suggestions["cities"] = list(set([item["city"] for item in city_result.data]))
        
        # Get neighborhood suggestions
        neighborhood_result = supabase.client.table("listings").select("neighborhood").ilike("neighborhood", f"%{q}%").limit(5).execute()
        if neighborhood_result.data:
            suggestions["neighborhoods"] = list(set([item["neighborhood"] for item in neighborhood_result.data]))
        
        # Get property type suggestions
        property_types = ["Apartment", "House", "Condo", "Townhouse", "Villa", "Studio", "Loft", "Penthouse"]
        suggestions["property_types"] = [pt for pt in property_types if q.lower() in pt.lower()]
        
        # Get amenity suggestions
        amenities = ["WiFi", "Air Conditioning", "Heating", "Kitchen", "Washing Machine", "Dryer", "Dishwasher", "Parking", "Gym", "Pool", "Garden", "Balcony", "Fireplace", "Elevator", "Doorman", "Security System", "Pet Friendly", "Furnished"]
        suggestions["amenities"] = [amenity for amenity in amenities if q.lower() in amenity.lower()]
        
        return suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.get("/stats")
async def get_search_stats():
    """Get search statistics and filters"""
    try:
        stats = {}
        
        # Get total listings count
        total_result = supabase.client.table("listings").select("id", count="exact").execute()
        stats["total_listings"] = total_result.count if total_result.count else 0
        
        # Get available listings count
        available_result = supabase.client.table("listings").select("id", count="exact").eq("is_available", True).execute()
        stats["available_listings"] = available_result.count if available_result.count else 0
        
        # Get featured listings count
        featured_result = supabase.client.table("listings").select("id", count="exact").eq("is_featured", True).execute()
        stats["featured_listings"] = featured_result.count if featured_result.count else 0
        
        # Get price range
        price_result = supabase.client.table("listings").select("price_per_night").execute()
        if price_result.data:
            prices = [item["price_per_night"] for item in price_result.data if item["price_per_night"]]
            stats["price_range"] = {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0
            }
        
        # Get cities count
        cities_result = supabase.client.table("listings").select("city").execute()
        if cities_result.data:
            stats["cities_count"] = len(set([item["city"] for item in cities_result.data]))
        
        # Get property types count
        types_result = supabase.client.table("listings").select("property_type").execute()
        if types_result.data:
            stats["property_types_count"] = len(set([item["property_type"] for item in types_result.data]))
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Placeholder for future RAG integration
@router.post("/ai-search")
async def ai_search(query: str):
    """AI-powered natural language search (RAG integration)"""
    # This will be implemented when RAG module is integrated
    return {
        "message": "AI search coming soon!",
        "query": query,
        "results": []
    } 