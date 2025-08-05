from fastapi import APIRouter, HTTPException, Query
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
class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_host: bool = False
    is_verified: bool = False

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_host: Optional[bool] = None
    is_verified: Optional[bool] = None

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    is_host: Optional[bool] = Query(None, description="Filter by host status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status")
):
    """Get all users with optional filters"""
    try:
        query = supabase.client.table("profiles").select("*")
        
        # Apply filters
        if is_host is not None:
            query = query.eq("is_host", is_host)
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
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a specific user by ID"""
    try:
        result = supabase.client.table("profiles").select("*").eq("id", user_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    """Get a user by email address"""
    try:
        result = supabase.client.table("profiles").select("*").eq("email", email).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        user_data = user.dict()
        user_data["created_at"] = datetime.now().isoformat()
        user_data["updated_at"] = datetime.now().isoformat()
        
        result = supabase.client.table("profiles").insert(user_data).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate):
    """Update an existing user"""
    try:
        update_data = user.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Update full_name if first_name or last_name changed
        if "first_name" in update_data or "last_name" in update_data:
            current_user = supabase.client.table("profiles").select("first_name, last_name").eq("id", user_id).execute()
            if current_user.data:
                first_name = update_data.get("first_name", current_user.data[0]["first_name"])
                last_name = update_data.get("last_name", current_user.data[0]["last_name"])
                update_data["full_name"] = f"{first_name} {last_name}"
        
        result = supabase.client.table("profiles").update(update_data).eq("id", user_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    try:
        result = supabase.client.table("profiles").delete().eq("id", user_id).execute()
        
        if result.data:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@router.get("/hosts/list", response_model=List[UserResponse])
async def get_hosts():
    """Get all users who are hosts"""
    try:
        result = supabase.client.table("profiles").select("*").eq("is_host", True).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hosts: {str(e)}")

@router.get("/verified/list", response_model=List[UserResponse])
async def get_verified_users():
    """Get all verified users"""
    try:
        result = supabase.client.table("profiles").select("*").eq("is_verified", True).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching verified users: {str(e)}")

@router.put("/{user_id}/verify")
async def verify_user(user_id: str):
    """Verify a user"""
    try:
        result = supabase.client.table("profiles").update({
            "is_verified": True,
            "updated_at": datetime.now().isoformat()
        }).eq("id", user_id).execute()
        
        if result.data:
            return {"message": "User verified successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying user: {str(e)}")

@router.put("/{user_id}/unverify")
async def unverify_user(user_id: str):
    """Unverify a user"""
    try:
        result = supabase.client.table("profiles").update({
            "is_verified": False,
            "updated_at": datetime.now().isoformat()
        }).eq("id", user_id).execute()
        
        if result.data:
            return {"message": "User unverified successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unverifying user: {str(e)}") 