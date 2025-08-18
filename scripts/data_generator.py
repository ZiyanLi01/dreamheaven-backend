from faker import Faker
import random
import os
import requests
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RealEstateDataGenerator:
    """Generate realistic real estate data for Dream Haven"""
    
    def __init__(self):
        self.fake = Faker()
        Faker.seed(42)  # For reproducible results
        
        # Real estate specific data
        self.property_types = [
            "Apartment", "House", "Condo", "Townhouse", "Villa", 
            "Studio", "Loft", "Penthouse", "Duplex", "Cottage"
        ]
        
        self.amenities = [
            "WiFi", "Air Conditioning", "Heating", "Kitchen", "Washing Machine",
            "Dryer", "Dishwasher", "Parking", "Gym", "Pool", "Garden", "Balcony",
            "Fireplace", "Elevator", "Doorman", "Security System", "Pet Friendly",
            "Furnished", "Balcony", "Mountain View", "Ocean View", "City View"
        ]
        
        self.cities = [
            {"name": "San Francisco", "state": "CA", "lat": 37.7749, "lng": -122.4194},
            {"name": "New York", "state": "NY", "lat": 40.7128, "lng": -74.0060},
            {"name": "Los Angeles", "state": "CA", "lat": 34.0522, "lng": -118.2437},
            {"name": "Chicago", "state": "IL", "lat": 41.8781, "lng": -87.6298},
            {"name": "Miami", "state": "FL", "lat": 25.7617, "lng": -80.1918},
            {"name": "Seattle", "state": "WA", "lat": 47.6062, "lng": -122.3321},
            {"name": "Austin", "state": "TX", "lat": 30.2672, "lng": -97.7431},
            {"name": "Denver", "state": "CO", "lat": 39.7392, "lng": -104.9903},
            {"name": "Portland", "state": "OR", "lat": 45.5152, "lng": -122.6784},
            {"name": "Nashville", "state": "TN", "lat": 36.1627, "lng": -86.7816}
        ]
        
        self.neighborhoods = [
            "Downtown", "Midtown", "Uptown", "Westside", "Eastside", 
            "North End", "South End", "Historic District", "Arts District",
            "Financial District", "University District", "Waterfront",
            "Hills", "Valley", "Heights", "Park", "Square", "Plaza"
        ]
    
    def generate_host(self) -> Dict[str, Any]:
        """Generate a fake host/user"""
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        
        return {
            "id": self.fake.uuid4(),
            "email": self.fake.email(),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "phone": self.fake.phone_number(),
            "avatar_url": self.fake.image_url(width=200, height=200),
            "bio": self.fake.text(max_nb_chars=200),
            "is_host": True,
            "is_verified": random.choice([True, False]),
            "created_at": self.fake.date_time_between(start_date="-2y", end_date="now").isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def generate_listing(self, host_id: str) -> Dict[str, Any]:
        """Generate a fake real estate listing with enhanced schema"""
        city = random.choice(self.cities)
        property_type = random.choice(self.property_types)
        
        # Determine property listing type based on property_type
        if property_type in ["Apartment", "Studio"]:
            property_listing_type = "rent"
        elif property_type in ["House", "Condo", "Townhouse", "Villa", "Penthouse", "Duplex", "Cottage"]:
            property_listing_type = "sale"
        else:
            property_listing_type = "sale"
        
        # Set some properties as both rent and sale (10% chance for eligible types)
        if property_type in ["House", "Condo", "Townhouse"] and random.random() < 0.1:
            property_listing_type = "both"
        
        # Generate realistic pricing based on property type and location
        base_price = self._get_base_price(property_type, city["name"])
        price_per_night = base_price + random.randint(-base_price//4, base_price//4)
        
        # Calculate sale and rent prices
        price_for_sale = None
        price_per_month = None
        
        if property_listing_type in ["sale", "both"]:
            # Convert nightly rate to annual sale price (30 nights * 12 months * multiplier)
            price_for_sale = price_per_night * 30 * 12 * random.uniform(0.8, 1.2)
        
        if property_listing_type in ["rent", "both"]:
            # Convert nightly rate to monthly rent (30 nights * multiplier)
            price_per_month = price_per_night * 30 * random.uniform(0.9, 1.1)
        
        # Generate realistic bedrooms and bathrooms
        if property_type in ["Studio", "Loft"]:
            bedrooms = 0
            bathrooms = random.randint(1, 2)
        elif property_type in ["Penthouse", "Villa", "House"]:
            bedrooms = random.randint(2, 5)
            bathrooms = random.randint(2, 4)
        else:
            bedrooms = random.randint(1, 3)
            bathrooms = random.randint(1, 3)
        
        # Generate square footage
        sqft = self._get_square_footage(property_type, bedrooms)
        
        # Generate garage number based on property type and size
        if property_type in ["House", "Villa"]:
            garage_number = 2 if sqft > 2000 else 1
        elif property_type in ["Condo", "Townhouse"]:
            garage_number = 1
        else:
            garage_number = 0
        
        # Generate yard availability
        has_yard = property_type in ["House", "Villa", "Cottage"] or (
            property_type == "Townhouse" and random.random() < 0.7
        )
        
        # Generate parking lot availability
        has_parking_lot = property_type in ["Apartment", "Condo", "Studio"] or (
            property_type in ["House", "Villa"] and random.random() < 0.3
        )
        
        # Generate amenities
        num_amenities = random.randint(3, 8)
        listing_amenities = random.sample(self.amenities, num_amenities)
        
        # Generate description
        description = self._generate_description(property_type, city, bedrooms, bathrooms, listing_amenities)
        
        # Generate images
        images = self._generate_images(property_type)
        
        return {
            "id": self.fake.uuid4(),
            "host_id": host_id,
            "title": self._generate_title(property_type, city, bedrooms),
            "description": description,
            "property_type": property_type,
            "property_listing_type": property_listing_type,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "max_guests": bedrooms * 2 + 1,
            "square_feet": sqft,
            "price_per_night": price_per_night,
            "price_per_month": price_per_month,
            "price_for_sale": price_for_sale,
            "city": city["name"],
            "state": city["state"],
            "country": "United States",
            "latitude": city["lat"] + random.uniform(-0.1, 0.1),
            "longitude": city["lng"] + random.uniform(-0.1, 0.1),
            "address": self.fake.street_address(),
            "neighborhood": random.choice(self.neighborhoods),
            "garage_number": garage_number,
            "has_yard": has_yard,
            "has_parking_lot": has_parking_lot,
            "amenities": listing_amenities,
            "images": images,
            "is_available": random.choice([True, True, True, False]),  # 75% available
            "is_featured": random.choice([True, False]),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "review_count": random.randint(0, 50),
            "created_at": self.fake.date_time_between(start_date="-1y", end_date="now").isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def generate_listing_v2(self, host_id: str) -> Dict[str, Any]:
        """Generate a fake real estate listing for listings_v2 schema (enhanced)"""
        city = random.choice(self.cities)
        property_type = random.choice(self.property_types)
        
        # Determine property listing type based on property_type
        if property_type in ["Apartment", "Studio"]:
            property_listing_type = "rent"
        elif property_type in ["House", "Condo", "Townhouse", "Villa", "Penthouse", "Duplex", "Cottage"]:
            property_listing_type = "sale"
        else:
            property_listing_type = "sale"
        
        # Set some properties as both rent and sale (10% chance for eligible types)
        if property_type in ["House", "Condo", "Townhouse"] and random.random() < 0.1:
            property_listing_type = "both"
        
        # Generate realistic pricing based on property type and location
        base_price = self._get_base_price(property_type, city["name"])
        price_per_night = base_price + random.randint(-base_price//4, base_price//4)
        
        # Calculate sale and rent prices
        price_for_sale = None
        price_per_month = None
        
        if property_listing_type in ["sale", "both"]:
            # Convert nightly rate to annual sale price (30 nights * 12 months * multiplier)
            price_for_sale = int(price_per_night * 30 * 12 * random.uniform(0.8, 1.2))
        
        if property_listing_type in ["rent", "both"]:
            # Convert nightly rate to monthly rent (30 nights * multiplier)
            price_per_month = int(price_per_night * 30 * random.uniform(0.9, 1.1))
        
        # Generate realistic bedrooms and bathrooms
        if property_type in ["Studio", "Loft"]:
            bedrooms = 0
            bathrooms = random.randint(1, 2)
        elif property_type in ["Penthouse", "Villa", "House"]:
            bedrooms = random.randint(2, 5)
            bathrooms = random.randint(2, 4)
        else:
            bedrooms = random.randint(1, 3)
            bathrooms = random.randint(1, 3)
        
        # Generate square footage
        sqft = self._get_square_footage(property_type, bedrooms)
        
        # Generate garage number based on property type and size
        if property_type in ["House", "Villa"]:
            garage_number = 2 if sqft > 2000 else 1
        elif property_type in ["Condo", "Townhouse"]:
            garage_number = 1
        else:
            garage_number = 0
        
        # Generate yard availability
        has_yard = property_type in ["House", "Villa", "Cottage"] or (
            property_type == "Townhouse" and random.random() < 0.7
        )
        
        # Generate parking lot availability
        has_parking_lot = property_type in ["Apartment", "Condo", "Studio"] or (
            property_type in ["House", "Villa"] and random.random() < 0.3
        )
        
        # Generate amenities
        num_amenities = random.randint(3, 8)
        listing_amenities = random.sample(self.amenities, num_amenities)
        
        # Generate additional v2 fields first (before description generation)
        floor = random.randint(1, 25) if property_type in ["Apartment", "Condo", "Penthouse"] and random.random() > 0.3 else None
        year_built = random.randint(1900, 2023) if random.random() > 0.2 else None
        year_renovated = random.randint(2010, 2023) if random.random() > 0.4 else None
        school_rating = random.randint(6, 10) if random.random() > 0.3 else None
        crime_index = round(random.uniform(20, 80), 1) if random.random() > 0.3 else None
        facing = random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]) if random.random() > 0.4 else None
        shopping_idx = round(random.uniform(60, 95), 1) if random.random() > 0.3 else None
        grocery_idx = round(random.uniform(70, 98), 1) if random.random() > 0.3 else None
        
        # Generate tags (initially empty - will be populated by ETL #1)
        tags = None
        
        # Generate description using ChatGPT API with all available property details
        description = self._generate_description(
            property_type=property_type,
            city=city,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            amenities=listing_amenities,
            square_feet=sqft,
            year_built=year_built,
            year_renovated=year_renovated,
            facing=facing,
            school_rating=school_rating,
            crime_index=crime_index,
            shopping_idx=shopping_idx,
            grocery_idx=grocery_idx,
            tags=tags
        )
        
        # Generate images (initially empty for v2 - will be filled later)
        images = None
        
        # Generate title using the existing method
        title = self._generate_title(property_type, city["name"], bedrooms)
        
        # Generate embedding text (initially empty - will be populated by ETL #2)
        embedding_text = ""
        
        return {
            "id": self.fake.uuid4(),
            "host_id": host_id,
            
            # Property classification
            "property_type": property_type,
            "property_listing_type": property_listing_type,
            
            # Basic property information (relaxed validation)
            "title": title,
            "description": description,
            "images": images,
            
            # Property specifications
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "square_feet": sqft,
            
            # Pricing (separate fields for rent and sale)
            "price_per_month": price_per_month,
            "price_for_sale": price_for_sale,
            
            # Location information
            "city": city["name"],
            "state": city["state"],
            "country": "United States",
            "latitude": city["lat"] + random.uniform(-0.1, 0.1),
            "longitude": city["lng"] + random.uniform(-0.1, 0.1),
            "address": self.fake.street_address(),
            "neighborhood": random.choice(self.neighborhoods),
            
            # Property features
            "garage_number": garage_number,
            "has_yard": has_yard,
            "has_parking_lot": has_parking_lot,
            "amenities": listing_amenities,
            
            # Property status
            "is_available": random.choice([True, True, True, False]),  # 75% available
            "is_featured": random.choice([True, False]),
            
            # Ratings and reviews
            "rating": round(random.uniform(3.5, 5.0), 1),
            "review_count": random.randint(5, 150),
            
            # Additional property details
            "floor": floor,
            "year_built": year_built,
            "year_renovated": year_renovated,
            "school_rating": school_rating,
            "crime_index": crime_index,
            "facing": facing,
            "shopping_idx": shopping_idx,
            "grocery_idx": grocery_idx,
            "tags": tags,
            
            # AI/ML fields
            "embedding_text": embedding_text,
            "embedding": None,  # Will be generated later if needed
            
            # Timestamps
            "created_at": self.fake.date_time_between(start_date="-1y", end_date="now").isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def _get_base_price(self, property_type: str, city: str) -> int:
        """Get base price based on property type and city"""
        city_multipliers = {
            "San Francisco": 2.5,
            "New York": 2.3,
            "Los Angeles": 2.0,
            "Chicago": 1.5,
            "Miami": 1.8,
            "Seattle": 1.7,
            "Austin": 1.3,
            "Denver": 1.4,
            "Portland": 1.2,
            "Nashville": 1.1
        }
        
        base_prices = {
            "Studio": 80,
            "Loft": 120,
            "Apartment": 100,
            "Condo": 150,
            "Townhouse": 200,
            "House": 250,
            "Villa": 400,
            "Penthouse": 500,
            "Duplex": 300,
            "Cottage": 180
        }
        
        base = base_prices.get(property_type, 150)
        multiplier = city_multipliers.get(city, 1.0)
        return int(base * multiplier)
    
    def _get_square_footage(self, property_type: str, bedrooms: int) -> int:
        """Get realistic square footage"""
        base_sqft = {
            "Studio": 400,
            "Loft": 600,
            "Apartment": 800,
            "Condo": 1000,
            "Townhouse": 1500,
            "House": 2000,
            "Villa": 3000,
            "Penthouse": 2500,
            "Duplex": 1800,
            "Cottage": 1200
        }
        
        base = base_sqft.get(property_type, 1000)
        bedroom_adjustment = bedrooms * 200
        return base + bedroom_adjustment + random.randint(-100, 200)
    
    def _generate_title(self, property_type: str, city: str, bedrooms: int) -> str:
        """Generate a compelling listing title"""
        adjectives = ["Beautiful", "Stunning", "Modern", "Cozy", "Luxurious", "Charming", "Spacious", "Elegant"]
        locations = ["Downtown", "Historic District", "Arts District", "Waterfront", "Hills", "Park"]
        
        adj = random.choice(adjectives)
        loc = random.choice(locations)
        
        if bedrooms == 0:
            return f"{adj} {property_type} in {loc} {city}"
        elif bedrooms == 1:
            return f"{adj} {bedrooms}-Bedroom {property_type} in {loc} {city}"
        else:
            return f"{adj} {bedrooms}-Bedroom {property_type} in {loc} {city}"
    
    def _generate_description(self, property_type: str, city: str, bedrooms: int, bathrooms: int, 
                            amenities: List[str], **kwargs) -> str:
        """Generate a detailed property description using ChatGPT API"""
        
        # Check if OpenAI API key is available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            # Return empty string if no API key
            return ""
        
        try:
            # Extract optional parameters from kwargs with default values
            square_feet = kwargs.get('square_feet')
            year_built = kwargs.get('year_built')
            year_renovated = kwargs.get('year_renovated')
            facing = kwargs.get('facing')
            school_rating = kwargs.get('school_rating')
            crime_index = kwargs.get('crime_index')
            shopping_idx = kwargs.get('shopping_idx')
            grocery_idx = kwargs.get('grocery_idx')
            tags = kwargs.get('tags', [])
            
            # Ensure all variables are defined
            if not isinstance(tags, list):
                tags = []
            
            # Prepare the prompt with all available property details
            property_details = {
                "property_type": property_type,
                "city": city["name"],
                "state": city["state"],
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "square_feet": square_feet,
                "year_built": year_built,
                "year_renovated": year_renovated,
                "facing": facing,
                "amenities": amenities[:5] if amenities else [],  # Limit to 5 amenities
                "school_rating": school_rating,
                "crime_index": crime_index,
                "shopping_idx": shopping_idx,
                "grocery_idx": grocery_idx,
                "tags": tags[:3] if tags else []  # Limit to 3 tags
            }
            
            # Create the user prompt with property details
            user_prompt = f"""
                Generate a property description for:
                - Property Type: {property_details['property_type']}
                - Location: {property_details['city']}, {property_details['state']}
                - Bedrooms: {property_details['bedrooms']}
                - Bathrooms: {property_details['bathrooms']}
                - Square Feet: {property_details['square_feet']}
                - Year Built: {property_details['year_built']}
                - Year Renovated: {property_details['year_renovated']}
                - Facing: {property_details['facing']}
                - Amenities: {', '.join(property_details['amenities'])}
                - School Rating: {property_details['school_rating']}/10
                - Crime Index: {property_details['crime_index']}/100
                - Shopping Index: {property_details['shopping_idx']}/100
                - Grocery Index: {property_details['grocery_idx']}/100
                - Tags: {', '.join(property_details['tags'])}
                """
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a real estate description generator.
Your task is to produce ONE property description in natural English.
Requirements:
- Maximum length: 200 words
- Marketing-friendly but factual
- Avoid exaggeration; keep concise and factual.
- Randomly choose a writing tone yourself (do not generate multiple versions)
- Seamlessly use the structured fields provided (sqft, renovated_year, facing, distance_to_metro, pet_friendly, etc.)
- If relevant, mention: safety, school quality, quietness, coffee density, grocery density, natural light, commuting convenience
- Return ONLY the description body. No lists, no headings, no explanations, no JSON."""
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            # Make the API call
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result["choices"][0]["message"]["content"].strip()
                return description
            else:
                print(f"  ChatGPT API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            print(f"  Error calling ChatGPT API: {str(e)}")
            return ""
    

    
    def _generate_images(self, property_type: str) -> List[str]:
        """Generate realistic image URLs"""
        num_images = random.randint(3, 8)
        images = []
        
        for i in range(num_images):
            # Use Lorem Picsum for reliable demo images
            width = random.choice([800, 1200, 1600])
            height = random.choice([600, 800, 1200])
            # Generate a random ID for consistent images
            image_id = random.randint(1, 1000)
            images.append(f"https://picsum.photos/{width}/{height}?random={image_id}")
        
        return images
    
    def generate_hosts(self, count: int) -> List[Dict[str, Any]]:
        """Generate multiple hosts"""
        return [self.generate_host() for _ in range(count)]
    
    def generate_listings(self, host_ids: List[str], count: int) -> List[Dict[str, Any]]:
        """Generate multiple listings distributed among hosts"""
        listings = []
        for _ in range(count):
            host_id = random.choice(host_ids)
            listings.append(self.generate_listing(host_id))
        return listings
    
    def generate_listings_v2(self, host_ids: List[str], count: int) -> List[Dict[str, Any]]:
        """Generate multiple listings for listings_v2 schema"""
        listings = []
        for i in range(count):
            host_id = random.choice(host_ids)
            listing = self.generate_listing_v2(host_id)
            listings.append(listing)
            print(f"✅ Generated listing_v2 {i+1}/{count}: {listing.get('title', 'Untitled')}")
        return listings 