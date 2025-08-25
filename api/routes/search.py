from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.config import Config
from scripts.supabase_manager import SupabaseManager

router = APIRouter()

# Lazy initialization of Supabase client
def get_supabase():
    try:
        return SupabaseManager()
    except Exception as e:
        print(f"Error initializing Supabase client: {str(e)}")
        return None
security = HTTPBearer()

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
    results: dict  # Changed from List[SearchResult] to dict with UUID keys
    total: int
    page: int
    limit: int
    has_more: bool

# Request model for POST search
class SearchRequest(BaseModel):
    location: Optional[str] = None
    bed: Optional[str] = None
    bath: Optional[str] = None
    rent: Optional[str] = None
    sortBy: Optional[str] = None
    sortOrder: Optional[str] = "asc"
    page: int = 1
    limit: Optional[int] = None  # Remove default limit to return all results

@router.post("/", response_model=SearchResponse)
async def search_listings_post(search_request: SearchRequest):
    """Search listings with POST request - returns paginated results"""
    try:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        # Build query with ALL fields from the listings_v2 table
        query = supabase.client.table("listings_v2").select("*")
        
        # Apply location filter
        if search_request.location:
            # Split location into city and state (e.g., "Los Angeles, CA")
            location_parts = search_request.location.split(',')
            if len(location_parts) == 2:
                city = location_parts[0].strip()
                state = location_parts[1].strip()
                query = query.eq("city", city).eq("state", state)
            else:
                # Fallback to just city if no comma found
                query = query.eq("city", search_request.location.strip())
        
        # Apply bedrooms filter
        if search_request.bed and search_request.bed != "Any":
            if search_request.bed.endswith("+"):
                # Handle patterns like "2+", "5+", etc.
                try:
                    min_beds = int(search_request.bed[:-1])  # Remove the "+" and convert to int
                    query = query.gte("bedrooms", min_beds)
                except ValueError:
                    # If parsing fails, skip this filter
                    pass
            else:
                try:
                    bed_count = int(search_request.bed)
                    query = query.eq("bedrooms", bed_count)
                except ValueError:
                    # If parsing fails, skip this filter
                    pass
        
        # Apply bathrooms filter
        if search_request.bath and search_request.bath != "Any":
            if search_request.bath.endswith("+"):
                # Handle patterns like "2+", "5+", etc.
                try:
                    min_baths = int(search_request.bath[:-1])  # Remove the "+" and convert to int
                    query = query.gte("bathrooms", min_baths)
                except ValueError:
                    # If parsing fails, skip this filter
                    pass
            else:
                try:
                    bath_count = int(search_request.bath)
                    query = query.eq("bathrooms", bath_count)
                except ValueError:
                    # If parsing fails, skip this filter
                    pass
        
        # Apply rent filter
        if search_request.rent:
            if search_request.rent == "For Rent":
                # Filter for properties with property_listing_type = 'rent' or 'both'
                query = query.in_("property_listing_type", ["rent", "both"])
            elif search_request.rent == "For Sale":
                # Filter for properties with property_listing_type = 'sale' or 'both'
                query = query.in_("property_listing_type", ["sale", "both"])
        
        # Apply sorting
        if search_request.sortBy:
            sort_direction = "asc" if search_request.sortOrder and search_request.sortOrder.lower() == "asc" else "desc"
            
            # Special handling for price sorting to consider both rent and sale prices
            if search_request.sortBy == "price":
                # For price sorting, we need to fetch all data first, sort it, then paginate
                print(f"Price sorting requested in AI search - will sort in Python after fetch")
            else:
                # For non-price sorting, use the standard approach
                sort_field_mapping = {
                    "bedrooms": "bedrooms",
                    "bathrooms": "bathrooms",
                    "square_feet": "square_feet"
                }
                
                db_sort_field = sort_field_mapping.get(search_request.sortBy, "bedrooms")
                if sort_direction == "asc":
                    query = query.order(db_sort_field, desc=False)
                else:
                    query = query.order(db_sort_field, desc=True)
        
        # Apply pagination to all queries (both price and non-price sorting)
        page = search_request.page
        limit = search_request.limit or 30  # Default to 30 items per page
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Apply pagination to database query
        result = query.range(start_idx, end_idx - 1).execute()
        
        if result.data:
            # Transform data to return full listing objects
            listings_dict = {}
            for item in result.data:
                # Return the full listing object as-is from the database
                # This includes all fields: id, title, description, property_type, property_listing_type,
                # bedrooms, bathrooms, square_feet, garage_number, price_per_month, price_for_sale,
                # city, state, country, latitude, longitude, address, neighborhood,
                # has_yard, has_parking_lot, amenities, images, is_available, is_featured, rating, review_count
                
                # Use the listing ID as the key in the dictionary
                listings_dict[item.get("id", "")] = item
            
            # Get total count for pagination info - NO RANGE LIMITS
            count_query = supabase.client.table("listings_v2").select("id", count="exact")
            
            # Apply the same filters to the count query
            if search_request.location:
                location_parts = search_request.location.split(',')
                if len(location_parts) == 2:
                    city = location_parts[0].strip()
                    state = location_parts[1].strip()
                    count_query = count_query.eq("city", city).eq("state", state)
                else:
                    count_query = count_query.eq("city", search_request.location.strip())
            
            if search_request.bed and search_request.bed != "Any":
                if search_request.bed.endswith("+"):
                    try:
                        min_beds = int(search_request.bed[:-1])
                        count_query = count_query.gte("bedrooms", min_beds)
                    except ValueError:
                        pass
                else:
                    try:
                        bed_count = int(search_request.bed)
                        count_query = count_query.eq("bedrooms", bed_count)
                    except ValueError:
                        pass
            
            if search_request.bath and search_request.bath != "Any":
                if search_request.bath.endswith("+"):
                    try:
                        min_baths = int(search_request.bath[:-1])
                        count_query = count_query.gte("bathrooms", min_baths)
                    except ValueError:
                        pass
                else:
                    try:
                        bath_count = int(search_request.bath)
                        count_query = count_query.eq("bathrooms", bath_count)
                    except ValueError:
                        pass
            
            if search_request.rent:
                if search_request.rent == "For Rent":
                    count_query = count_query.in_("property_listing_type", ["rent", "both"])
                elif search_request.rent == "For Sale":
                    count_query = count_query.in_("property_listing_type", ["sale", "both"])
            
            # Execute count query without any range limits
            total_result = count_query.execute()
            total_count = total_result.count if hasattr(total_result, 'count') else 0
            
            # Check if there are more results
            has_more = end_idx < total_count
            
            return SearchResponse(
                results=listings_dict,
                total=total_count,
                page=page,
                limit=len(result.data),
                has_more=has_more
            )
        else:
            return SearchResponse(
                results={},
                total=0,
                page=1,
                limit=0,
                has_more=False
            )
            
    except Exception as e:
        print(f"Error in search_listings_post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

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
    sort_by: str = Query("created_at", description="Sort by field (price_per_month, rating, created_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(None, ge=1, description="Number of results per page (None = all results)")
):
    """Search listings with various filters and sorting options"""
    try:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        # Build query
        query = supabase.client.table("listings_v2").select("*")
        
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
            query = query.gte("price_per_month", min_price)
        if max_price is not None:
            query = query.lte("price_per_month", max_price)
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
        
        # Apply pagination
        start_idx = (page - 1) * (limit or 30)
        end_idx = start_idx + (limit or 30) - 1
        
        # Execute query with pagination
        result = query.range(start_idx, end_idx).execute()
        listings = result.data if result.data else []
        
        # Get total count for pagination info - NO RANGE LIMITS
        count_query = supabase.client.table("listings_v2").select("id", count="exact")
        
        # Apply the same filters to the count query
        if q:
            count_query = count_query.or_(f"title.ilike.%{q}%,description.ilike.%{q}%,city.ilike.%{q}%,neighborhood.ilike.%{q}%")
        if city:
            count_query = count_query.eq("city", city)
        if state:
            count_query = count_query.eq("state", state)
        if property_type:
            count_query = count_query.eq("property_type", property_type)
        if min_price is not None:
            count_query = count_query.gte("price_per_month", min_price)
        if max_price is not None:
            count_query = count_query.lte("price_per_month", max_price)
        if min_bedrooms is not None:
            count_query = count_query.gte("bedrooms", min_bedrooms)
        if max_bedrooms is not None:
            count_query = count_query.lte("bedrooms", max_bedrooms)
        if min_bathrooms is not None:
            count_query = count_query.gte("bathrooms", min_bathrooms)
        if available_only:
            count_query = count_query.eq("is_available", True)
        if featured_only:
            count_query = count_query.eq("is_featured", True)
        
        # Execute count query without any range limits
        total_result = count_query.execute()
        total = total_result.count if hasattr(total_result, 'count') else 0
        
        # Filter by amenities if specified (apply to current page only)
        if amenities:
            amenity_list = [a.strip() for a in amenities.split(",")]
            filtered_listings = []
            for listing in listings:
                if listing.get("amenities"):
                    listing_amenities = listing["amenities"]
                    if any(amenity in listing_amenities for amenity in amenity_list):
                        filtered_listings.append(listing)
            listings = filtered_listings
        
        # Transform to dictionary format
        listings_dict = {}
        for listing in listings:
            listings_dict[listing.get("id", "")] = listing
        
        # Check if there are more results
        has_more = end_idx + 1 < total
        
        return SearchResponse(
            results=listings_dict,
            total=total,
            page=page,
            limit=len(listings),
            has_more=has_more
        )
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/nearby", response_model=List[SearchResult])
async def search_nearby(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius_km: float = Query(10.0, ge=0.1, le=100.0, description="Search radius in kilometers"),
    limit: Optional[int] = Query(None, ge=1, description="Number of results (None = all results)")
):
    """Search for listings near a specific location"""
    try:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        # Convert radius from km to degrees (approximate)
        # 1 degree ≈ 111 km
        radius_degrees = radius_km / 111.0
        
        # Calculate bounding box
        lat_min = latitude - radius_degrees
        lat_max = latitude + radius_degrees
        lng_min = longitude - radius_degrees
        lng_max = longitude + radius_degrees
        
        # Query listings within bounding box
        query = supabase.client.table("listings_v2").select("*").eq("is_available", True)
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

@router.get("/health")
async def search_health_check():
    """Health check for search service"""
    try:
        supabase = get_supabase()
        if not supabase:
            return {"status": "error", "message": "Database connection not available"}
        
        # Test a simple query
        result = supabase.client.table("listings_v2").select("id", count="exact").execute()
        count = result.count if hasattr(result, 'count') else 0
        
        return {
            "status": "healthy", 
            "message": "Search service is working",
            "listings_count": count
        }
    except Exception as e:
        return {"status": "error", "message": f"Database error: {str(e)}"}

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Search query for suggestions")
):
    """Get search suggestions based on partial query"""
    try:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        suggestions = {
            "cities": [],
            "neighborhoods": [],
            "property_types": [],
            "amenities": []
        }
        
        # Get city suggestions
        city_result = supabase.client.table("listings_v2").select("city").ilike("city", f"%{q}%").limit(5).execute()
        if city_result.data:
            suggestions["cities"] = list(set([item["city"] for item in city_result.data]))
        
        # Get neighborhood suggestions
        neighborhood_result = supabase.client.table("listings_v2").select("neighborhood").ilike("neighborhood", f"%{q}%").limit(5).execute()
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
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        stats = {}
        
        # Get total listings count
        total_result = supabase.client.table("listings_v2").select("id", count="exact").execute()
        stats["total_listings"] = total_result.count if total_result.count else 0
        
        # Get available listings count
        available_result = supabase.client.table("listings_v2").select("id", count="exact").eq("is_available", True).execute()
        stats["available_listings"] = available_result.count if available_result.count else 0
        
        # Get featured listings count
        featured_result = supabase.client.table("listings_v2").select("id", count="exact").eq("is_featured", True).execute()
        stats["featured_listings"] = featured_result.count if featured_result.count else 0
        
        # Get price range
        price_result = supabase.client.table("listings_v2").select("price_per_month").execute()
        if price_result.data:
            prices = [item["price_per_month"] for item in price_result.data if item["price_per_month"]]
            stats["price_range"] = {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0
            }
        
        # Get cities count
        cities_result = supabase.client.table("listings_v2").select("city").execute()
        if cities_result.data:
            stats["cities_count"] = len(set([item["city"] for item in cities_result.data]))
        
        # Get property types count
        types_result = supabase.client.table("listings_v2").select("property_type").execute()
        if types_result.data:
            stats["property_types_count"] = len(set([item["property_type"] for item in types_result.data]))
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Placeholder for future RAG integration
@router.post("/ai-search")
async def ai_search(
    query: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """AI-powered natural language search (RAG integration) - Requires authentication"""
    try:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        # Verify authentication
        supabase.client.auth.set_session(credentials.credentials, None)
        user = supabase.client.auth.get_user()
        
        if not user.user:
            raise HTTPException(status_code=401, detail="Authentication required for AI search")
        
        # This will be implemented when RAG module is integrated
        return {
            "message": "AI search coming soon!",
            "query": query,
            "results": [],
            "user_id": user.user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication required for AI search") 