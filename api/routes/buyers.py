from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
security = HTTPBearer()

# Pydantic models
class BuyerBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str] = None
    preferences: Optional[dict] = None
    is_verified: bool = False

class BuyerCreate(BuyerBase):
    pass

class BuyerResponse(BuyerBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BuyerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[dict] = None
    is_verified: Optional[bool] = None

class BuyerPreferences(BaseModel):
    preferred_cities: Optional[List[str]] = None
    preferred_property_types: Optional[List[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    preferred_amenities: Optional[List[str]] = None

@router.get("/", response_model=List[BuyerResponse])
async def get_buyers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status")
):
    """Get all buyers with optional filters"""
    try:
        query = supabase.client.table("buyers").select("*")
        
        # Apply filters
        if is_verified is not None:
            query = query.eq("is_verified", is_verified)
        
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        result = query.execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching buyers: {str(e)}")

@router.get("/{buyer_id}", response_model=BuyerResponse)
async def get_buyer(buyer_id: str):
    """Get a specific buyer by ID"""
    try:
        result = supabase.client.table("buyers").select("*").eq("id", buyer_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Buyer not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching buyer: {str(e)}")

@router.get("/email/{email}", response_model=BuyerResponse)
async def get_buyer_by_email(email: str):
    """Get a buyer by email address"""
    try:
        result = supabase.client.table("buyers").select("*").eq("email", email).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Buyer not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching buyer: {str(e)}")

@router.put("/{buyer_id}", response_model=BuyerResponse)
async def update_buyer(buyer_id: str, buyer: BuyerUpdate):
    """Update an existing buyer"""
    try:
        update_data = buyer.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Update full_name if first_name or last_name changed
        if "first_name" in update_data or "last_name" in update_data:
            current_buyer = supabase.client.table("buyers").select("first_name, last_name").eq("id", buyer_id).execute()
            if current_buyer.data:
                first_name = update_data.get("first_name", current_buyer.data[0]["first_name"])
                last_name = update_data.get("last_name", current_buyer.data[0]["last_name"])
                update_data["full_name"] = f"{first_name} {last_name}"
        
        result = supabase.client.table("buyers").update(update_data).eq("id", buyer_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Buyer not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating buyer: {str(e)}")

@router.put("/{buyer_id}/preferences")
async def update_buyer_preferences(buyer_id: str, preferences: BuyerPreferences):
    """Update buyer search preferences"""
    try:
        update_data = {
            "preferences": preferences.dict(exclude_unset=True),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.client.table("buyers").update(update_data).eq("id", buyer_id).execute()
        
        if result.data:
            return {"message": "Preferences updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Buyer not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")

@router.get("/{buyer_id}/preferences")
async def get_buyer_preferences(buyer_id: str):
    """Get buyer search preferences"""
    try:
        result = supabase.client.table("buyers").select("preferences").eq("id", buyer_id).execute()
        
        if result.data and result.data[0].get("preferences"):
            return result.data[0]["preferences"]
        else:
            return {}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching preferences: {str(e)}")

@router.delete("/{buyer_id}")
async def delete_buyer(buyer_id: str):
    """Delete a buyer"""
    try:
        result = supabase.client.table("buyers").delete().eq("id", buyer_id).execute()
        
        if result.data:
            return {"message": "Buyer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Buyer not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting buyer: {str(e)}")

@router.get("/verified/list", response_model=List[BuyerResponse])
async def get_verified_buyers():
    """Get all verified buyers"""
    try:
        result = supabase.client.table("buyers").select("*").eq("is_verified", True).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching verified buyers: {str(e)}")

@router.put("/{buyer_id}/verify")
async def verify_buyer(buyer_id: str):
    """Verify a buyer"""
    try:
        result = supabase.client.table("buyers").update({
            "is_verified": True,
            "updated_at": datetime.now().isoformat()
        }).eq("id", buyer_id).execute()
        
        if result.data:
            return {"message": "Buyer verified successfully"}
        else:
            raise HTTPException(status_code=404, detail="Buyer not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying buyer: {str(e)}")

@router.put("/{buyer_id}/unverify")
async def unverify_buyer(buyer_id: str):
    """Unverify a buyer"""
    try:
        result = supabase.client.table("buyers").update({
            "is_verified": False,
            "updated_at": datetime.now().isoformat()
        }).eq("id", buyer_id).execute()
        
        if result.data:
            return {"message": "Buyer unverified successfully"}
        else:
            raise HTTPException(status_code=404, detail="Buyer not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unverifying buyer: {str(e)}") 