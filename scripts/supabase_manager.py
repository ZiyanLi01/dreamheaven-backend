from supabase import Client
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from .config import Config

class SupabaseManager:
    """Manage Supabase database operations for Dream Haven"""
    
    def __init__(self):
        self.client = Config.get_supabase_client()
        self.anon_client = Config.get_supabase_anon_client()
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a user in profiles table (demo only, no auth)"""
        try:
            # Generate a UUID for the user
            import uuid
            user_id = str(uuid.uuid4())
            
            # Create profile in profiles table
            profile_data = {
                "id": user_id,
                "email": user_data["email"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "full_name": user_data["full_name"],
                "phone": user_data["phone"],
                "avatar_url": user_data["avatar_url"],
                "bio": user_data["bio"],
                "is_host": user_data["is_host"],
                "is_verified": user_data["is_verified"],
                "created_at": user_data["created_at"],
                "updated_at": user_data["updated_at"]
            }
            
            result = self.client.table("profiles").insert(profile_data).execute()
            
            print(f"✅ Created demo user: {user_data['email']}")
            return {
                "auth_user": type('User', (), {'id': user_id})(),
                "profile": result.data[0] if result.data else None
            }
            
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {str(e)}")
            raise
    
    def create_users_batch(self, users_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple users in batch"""
        created_users = []
        
        for user_data in users_data:
            try:
                result = self.create_user(user_data)
                created_users.append(result)
            except Exception as e:
                print(f"❌ Failed to create user {user_data['email']}: {str(e)}")
                continue
        
        print(f"✅ Successfully created {len(created_users)} out of {len(users_data)} users")
        return created_users
    
    def create_listing(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a listing in the listings_v2 table"""
        try:
            # Prepare listing data for database
            db_listing = {
                "id": listing_data["id"],
                "host_id": listing_data["host_id"],
                "title": listing_data["title"],
                "description": listing_data["description"],
                "property_type": listing_data["property_type"],
                "property_listing_type": listing_data["property_listing_type"],
                "bedrooms": listing_data["bedrooms"],
                "bathrooms": listing_data["bathrooms"],
                "square_feet": listing_data["square_feet"],
                "price_per_month": listing_data["price_per_month"],
                "price_for_sale": listing_data["price_for_sale"],
                "city": listing_data["city"],
                "state": listing_data["state"],
                "country": listing_data["country"],
                "latitude": listing_data["latitude"],
                "longitude": listing_data["longitude"],
                "address": listing_data["address"],
                "neighborhood": listing_data["neighborhood"],
                "garage_number": listing_data.get("garage_number"),
                "has_yard": listing_data.get("has_yard", False),
                "has_parking_lot": listing_data.get("has_parking_lot", False),
                "amenities": listing_data["amenities"],
                "images": listing_data["images"],
                "is_available": listing_data["is_available"],
                "is_featured": listing_data["is_featured"],
                "rating": listing_data.get("rating"),
                "review_count": listing_data.get("review_count"),
                "embedding_text": listing_data.get("embedding_text", ""),
                "created_at": listing_data["created_at"],
                "updated_at": listing_data["updated_at"]
            }
            
            result = self.client.table("listings_v2").insert(db_listing).execute()
            
            if result.data:
                print(f"✅ Created listing: {listing_data['title']}")
                return result.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            print(f"❌ Error creating listing {listing_data['title']}: {str(e)}")
            raise
    
    def create_listings_batch(self, listings_data: List[Dict[str, Any]], batch_size: int = 50) -> List[Dict[str, Any]]:
        """Create multiple listings in batches"""
        created_listings = []
        total_listings = len(listings_data)
        
        for i in range(0, total_listings, batch_size):
            batch = listings_data[i:i + batch_size]
            
            try:
                # Prepare batch data
                batch_data = []
                for listing in batch:
                    db_listing = {
                        "id": listing["id"],
                        "host_id": listing["host_id"],
                        "title": listing["title"],
                        "description": listing["description"],
                        "property_type": listing["property_type"],
                        "property_listing_type": listing["property_listing_type"],
                        "bedrooms": listing["bedrooms"],
                        "bathrooms": listing["bathrooms"],
                        "square_feet": listing["square_feet"],
                        "price_per_month": listing["price_per_month"],
                        "price_for_sale": listing["price_for_sale"],
                        "city": listing["city"],
                        "state": listing["state"],
                        "country": listing["country"],
                        "latitude": listing["latitude"],
                        "longitude": listing["longitude"],
                        "address": listing["address"],
                        "neighborhood": listing["neighborhood"],
                        "garage_number": listing.get("garage_number"),
                        "has_yard": listing.get("has_yard", False),
                        "has_parking_lot": listing.get("has_parking_lot", False),
                        "amenities": listing["amenities"],
                        "images": listing["images"],
                        "is_available": listing["is_available"],
                        "is_featured": listing["is_featured"],
                        "rating": listing.get("rating"),
                        "review_count": listing.get("review_count"),
                        "embedding_text": listing.get("embedding_text", ""),
                        "created_at": listing["created_at"],
                        "updated_at": listing["updated_at"]
                    }
                    batch_data.append(db_listing)
                
                result = self.client.table("listings_v2").insert(batch_data).execute()
                
                if result.data:
                    created_listings.extend(result.data)
                    print(f"✅ Created batch {i//batch_size + 1}: {len(result.data)} listings")
                else:
                    print(f"❌ No data returned for batch {i//batch_size + 1}")
                    
            except Exception as e:
                print(f"❌ Error creating batch {i//batch_size + 1}: {str(e)}")
                continue
        
        print(f"✅ Successfully created {len(created_listings)} out of {total_listings} listings")
        return created_listings
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from the profiles table"""
        try:
            result = self.client.table("profiles").select("*").execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Error fetching users: {str(e)}")
            return []
    
    def get_all_listings(self) -> List[Dict[str, Any]]:
        """Get all listings from the listings_v2 table"""
        try:
            result = self.client.table("listings_v2").select("*").execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Error fetching listings: {str(e)}")
            return []
    
    def get_listings_by_host(self, host_id: str) -> List[Dict[str, Any]]:
        """Get all listings for a specific host"""
        try:
            result = self.client.table("listings_v2").select("*").eq("host_id", host_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Error fetching listings for host {host_id}: {str(e)}")
            return []
    
    def delete_all_data(self):
        """Delete all data from listings_v2 and profiles tables (for testing)"""
        try:
            # Delete listings first (due to foreign key constraints)
            self.client.table("listings_v2").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("✅ Deleted all listings from listings_v2")
            
            # Note: We don't delete profiles as they're linked to auth users
            print("⚠️  Skipping profiles deletion (linked to auth users)")
            
        except Exception as e:
            print(f"❌ Error deleting data: {str(e)}")
    
    def create_database_schema(self):
        """Create the necessary database tables if they don't exist"""
        # This would typically be done via Supabase migrations
        # For now, we'll assume the tables exist
        print("ℹ️  Please ensure the following tables exist in your Supabase database:")
        print("   - profiles (id, email, first_name, last_name, full_name, phone, avatar_url, bio, is_host, is_verified, created_at, updated_at)")
        print("   - listings_v2 (id, host_id, title, description, property_type, property_listing_type, bedrooms, bathrooms, square_feet, price_per_month, price_for_sale, city, state, country, latitude, longitude, address, neighborhood, garage_number, has_yard, has_parking_lot, amenities, images, is_available, is_featured, rating, review_count, embedding_text, created_at, updated_at)") 