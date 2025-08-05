from faker import Faker
import random
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta

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
        """Generate a fake real estate listing"""
        city = random.choice(self.cities)
        property_type = random.choice(self.property_types)
        
        # Generate realistic pricing based on property type and location
        base_price = self._get_base_price(property_type, city["name"])
        price = base_price + random.randint(-base_price//4, base_price//4)
        
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
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "max_guests": bedrooms * 2 + 1,
            "square_feet": sqft,
            "price_per_night": price,
            "price_per_month": price * 30,
            "city": city["name"],
            "state": city["state"],
            "country": "United States",
            "latitude": city["lat"] + random.uniform(-0.1, 0.1),
            "longitude": city["lng"] + random.uniform(-0.1, 0.1),
            "address": self.fake.street_address(),
            "neighborhood": random.choice(self.neighborhoods),
            "amenities": listing_amenities,
            "images": images,
            "is_available": random.choice([True, True, True, False]),  # 75% available
            "is_featured": random.choice([True, False]),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "review_count": random.randint(0, 50),
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
    
    def _generate_description(self, property_type: str, city: str, bedrooms: int, bathrooms: int, amenities: List[str]) -> str:
        """Generate a detailed property description"""
        descriptions = [
            f"Welcome to this stunning {property_type.lower()} in the heart of {city['name']}! ",
            f"Experience luxury living in this beautiful {property_type.lower()} located in {city['name']}. ",
            f"Discover your perfect home in this charming {property_type.lower()} in {city['name']}. ",
            f"This exceptional {property_type.lower()} offers the best of {city['name']} living. "
        ]
        
        desc = random.choice(descriptions)
        
        if bedrooms > 0:
            desc += f"Featuring {bedrooms} spacious bedroom{'s' if bedrooms > 1 else ''} and {bathrooms} modern bathroom{'s' if bathrooms > 1 else ''}. "
        else:
            desc += f"Featuring {bathrooms} modern bathroom{'s' if bathrooms > 1 else ''}. "
        
        # Add amenities
        if amenities:
            amenity_text = ", ".join(amenities[:5])  # Limit to first 5 amenities
            desc += f"This property includes {amenity_text}. "
        
        desc += "Perfect for both short-term stays and long-term rentals. Don't miss this opportunity to experience the best of what this vibrant city has to offer!"
        
        return desc
    
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