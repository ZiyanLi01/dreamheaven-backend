from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
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
class BuyerLogin(BaseModel):
    email: EmailStr
    password: str

class BuyerRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    preferences: Optional[dict] = None  # For saving search preferences

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict
    expires_in: int

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    password: str

@router.post("/login", response_model=AuthResponse)
async def login(buyer_credentials: BuyerLogin):
    """Buyer login with email and password"""
    try:
        # Authenticate with Supabase
        auth_response = supabase.client.auth.sign_in_with_password({
            "email": buyer_credentials.email,
            "password": buyer_credentials.password
        })
        
        if auth_response.user:
            # Get user profile
            profile_result = supabase.client.table("profiles").select("*").eq("id", auth_response.user.id).execute()
            user_profile = profile_result.data[0] if profile_result.data else None
            
            return AuthResponse(
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                user=user_profile or {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email
                },
                expires_in=auth_response.session.expires_in
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register", response_model=AuthResponse)
async def register(buyer_data: BuyerRegister):
    """Buyer registration"""
    try:
        # Create buyer in Supabase Auth
        auth_response = supabase.client.auth.sign_up({
            "email": buyer_data.email,
            "password": buyer_data.password,
            "options": {
                "data": {
                    "first_name": buyer_data.first_name,
                    "last_name": buyer_data.last_name,
                    "user_type": "buyer"
                }
            }
        })
        
        if auth_response.user:
            # Create buyer profile in buyers table
            buyer_profile_data = {
                "id": auth_response.user.id,
                "email": buyer_data.email,
                "first_name": buyer_data.first_name,
                "last_name": buyer_data.last_name,
                "full_name": f"{buyer_data.first_name} {buyer_data.last_name}",
                "phone": buyer_data.phone,
                "preferences": buyer_data.preferences or {},
                "is_verified": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            buyer_result = supabase.client.table("buyers").insert(buyer_profile_data).execute()
            buyer_profile = buyer_result.data[0] if buyer_result.data else buyer_profile_data
            
            return AuthResponse(
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                user=buyer_profile,
                expires_in=auth_response.session.expires_in
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """User logout"""
    try:
        # Sign out from Supabase
        supabase.client.auth.sign_out()
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        # Refresh session with Supabase
        auth_response = supabase.client.auth.refresh_session(refresh_token)
        
        if auth_response.user:
            # Get user profile
            profile_result = supabase.client.table("profiles").select("*").eq("id", auth_response.user.id).execute()
            user_profile = profile_result.data[0] if profile_result.data else None
            
            return AuthResponse(
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                user=user_profile or {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email
                },
                expires_in=auth_response.session.expires_in
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        # Set the session with the access token
        supabase.client.auth.set_session(credentials.credentials, None)
        
        # Get current user
        user = supabase.client.auth.get_user()
        
        if user.user:
            # Get user profile
            profile_result = supabase.client.table("profiles").select("*").eq("id", user.user.id).execute()
            user_profile = profile_result.data[0] if profile_result.data else None
            
            return user_profile or {
                "id": user.user.id,
                "email": user.user.email
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/forgot-password")
async def forgot_password(password_reset: PasswordReset):
    """Send password reset email"""
    try:
        # Send password reset email via Supabase
        supabase.client.auth.reset_password_email(password_reset.email)
        return {"message": "Password reset email sent"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reset email: {str(e)}")

@router.post("/reset-password")
async def reset_password(token: str, password_update: PasswordUpdate):
    """Reset password with token"""
    try:
        # Update password with Supabase
        supabase.client.auth.update_user({"password": password_update.password})
        return {"message": "Password updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update password: {str(e)}")

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Change password for authenticated user"""
    try:
        # Set the session with the access token
        supabase.client.auth.set_session(credentials.credentials, None)
        
        # Update password
        supabase.client.auth.update_user({"password": new_password})
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to change password: {str(e)}")

@router.post("/verify-email")
async def verify_email(token: str):
    """Verify email address"""
    try:
        # Verify email with Supabase
        supabase.client.auth.verify_otp({
            "token_hash": token,
            "type": "email"
        })
        return {"message": "Email verified successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify email: {str(e)}")

@router.post("/resend-verification")
async def resend_verification_email(email: EmailStr):
    """Resend verification email"""
    try:
        # Resend verification email via Supabase
        supabase.client.auth.resend_signup_email(email)
        return {"message": "Verification email sent"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}") 