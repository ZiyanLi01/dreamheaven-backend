# Dream Haven Backend

A modern FastAPI backend for the Dream Haven real estate platform, featuring AI-powered search capabilities and comprehensive property management.

## Overview

Dream Haven Backend is a production-ready REST API built with FastAPI that provides:

- **High-performance property search** with advanced filtering and sorting
- **User authentication and authorization** for buyers
- **Real-time database operations** via Supabase
- **AI-ready architecture** for future RAG integration
- **Comprehensive property management** with 3000+ sample listings

## Key Features

- **FastAPI Backend**: High-performance REST API with automatic OpenAPI documentation
- **Supabase Integration**: PostgreSQL database with real-time capabilities and built-in authentication
- **Advanced Search**: Filter by location, price, bedrooms, bathrooms, and property type
- **Pagination**: Server-side pagination with configurable page sizes
- **Authentication**: Complete buyer authentication and authorization system
- **Data Generation**: Automated creation of realistic real estate data
- **Production Ready**: Clean, optimized codebase ready for deployment

## User Roles

### Hosts (Property Owners)
- Property owners who list their properties
- Managed directly in the database
- Currently: 5 demo hosts with 3000+ listings

### Buyers (Property Seekers)
- People looking to buy/rent properties
- Require authentication for advanced features
- Can browse listings without login
- Need login for AI-powered search

### Visitors
- Anonymous users browsing listings
- No authentication required
- Access to basic search and filtering

## Project Structure

```
dreamheaven-backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Production dependencies
├── env.example            # Environment variables template
├── start.sh               # Production startup script
├── DEPLOYMENT_CHECKLIST.md # Deployment guide
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── api/                   # Core API routes
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py        # Authentication endpoints
│       ├── buyers.py      # Buyer management
│       ├── listings.py    # Property listings CRUD
│       └── search.py      # Search functionality
└── scripts/               # Maintenance utilities
    ├── __init__.py
    ├── config.py          # Configuration management
    ├── data_generator.py  # Real estate data generation
    ├── supabase_manager.py # Database operations
    ├── generate_data.py   # Main data generation script
    └── upgrade_images.py  # Image management utilities
```

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Supabase account and project
- pip (Python package manager)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd dreamheaven-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your Supabase credentials
nano .env
```

Required environment variables:
```bash
# Supabase Configuration (REQUIRED)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Optional: Database URL for direct access
DATABASE_URL=postgresql://postgres:password@localhost:5432/dreamhaven

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Database Setup

The backend uses Supabase for database management. Ensure your Supabase project has the following tables:

#### Listings Table (listings_v2)
Contains all property listings with fields for:
- Basic property info (title, description, type)
- Location data (address, city, state, coordinates)
- Property details (bedrooms, bathrooms, square feet)
- Pricing (price_per_month for rentals, price_for_sale for sales)
- Features (amenities, parking, yard)
- Status (available, featured)

#### Buyers Table
Contains authenticated buyer information:
- User profile data (name, email, phone)
- Preferences and settings
- Verification status

#### Profiles Table
Linked to Supabase Auth for user management.

### 5. Data Generation

Generate sample data for testing:

```bash
# Generate hosts and listings
python scripts/generate_data.py

# Generate only hosts
python scripts/generate_data.py hosts

# Generate only listings (requires existing hosts)
python scripts/generate_data.py listings

# Clean up all data
python scripts/generate_data.py cleanup

# Show help
python scripts/generate_data.py help
```

### 6. Run the Application

```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or use the startup script
./start.sh
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Core Endpoints
- `GET /` - Welcome message and API info
- `GET /health` - Health check endpoint
- `GET /debug` - Debug information and database status

### Authentication (`/auth`)
- `POST /register` - Buyer registration
- `POST /login` - Buyer login
- `POST /logout` - Buyer logout
- `POST /refresh` - Refresh access token
- `GET /me` - Get current buyer profile
- `POST /forgot-password` - Send password reset email
- `POST /reset-password` - Reset password
- `POST /change-password` - Change password
- `POST /verify-email` - Verify email address

### Buyers (`/buyers`)
- `GET /` - Get all buyers with optional filters
- `GET /{buyer_id}` - Get specific buyer
- `GET /email/{email}` - Get buyer by email
- `PUT /{buyer_id}` - Update buyer profile
- `DELETE /{buyer_id}` - Delete buyer
- `GET /verified/list` - Get verified buyers
- `PUT /{buyer_id}/verify` - Verify buyer
- `PUT /{buyer_id}/unverify` - Unverify buyer
- `PUT /{buyer_id}/preferences` - Update buyer preferences
- `GET /{buyer_id}/preferences` - Get buyer preferences

### Listings (`/listings`)
- `GET /` - Get filtered property listings with pagination
  - **Query Parameters:**
    - `location` (optional) - Filter by city/location
    - `bedrooms` (optional, int) - Filter by number of bedrooms
    - `bathrooms` (optional, int) - Filter by number of bathrooms
    - `status` (optional) - Filter by status ("For Sale" or "For Rent")
    - `page` (default: 1) - Page number for pagination
    - `limit` (default: 30) - Number of records per page
  - **Response Format:**
    ```json
    {
      "results": {
        "listing_id": {
          "id": "uuid",
          "status": "For Sale",
          "address": "123 Main St",
          "location": "New York, NY",
          "sqft": 1500,
          "garages": 2,
          "bedrooms": 3,
          "bathrooms": 2,
          "agent": "John Doe",
          "listingAge": "2 days",
          "price": 750000,
          "imageUrl": "https://example.com/image.jpg"
        }
      },
      "page": 1,
      "limit": 30,
      "total": 150,
      "has_more": true
    }
    ```
- `GET /{listing_id}` - Get specific listing details
- `GET /types` - Get available property types

### Search (`/search`)
- `GET /` - Search listings with query parameters
  - **Query Parameters:**
    - `q` (optional) - Search query for title, description, city, neighborhood
    - `city`, `state` (optional) - Location filters
    - `property_type` (optional) - Property type filter
    - `min_price`, `max_price` (optional) - Price range filters
    - `min_bedrooms`, `max_bedrooms` (optional) - Bedroom range filters
    - `min_bathrooms` (optional) - Minimum bathrooms filter
    - `amenities` (optional) - Comma-separated amenities list
    - `available_only` (default: true) - Show only available listings
    - `featured_only` (default: false) - Show only featured listings
    - `sort_by` (default: "created_at") - Sort field
    - `sort_order` (default: "desc") - Sort direction (asc/desc)
    - `page` (default: 1) - Page number
    - `limit` (default: 30) - Results per page

- `POST /` - AI-powered search with advanced filters
  - **Request Body:**
    ```json
    {
      "query": "luxury apartments in downtown",
      "location": "San Francisco, CA",
      "bed": "2+",
      "bath": "2",
      "rent": "For Rent",
      "sortBy": "price",
      "sortOrder": "asc",
      "page": 1,
      "limit": 30
    }
    ```

## Data Management

### Sample Data
The backend includes comprehensive sample data:
- **3000+ property listings** across multiple cities
- **5 demo hosts** with realistic profiles
- **Diverse property types**: Apartments, houses, condos, townhouses
- **Realistic pricing** for both rentals and sales
- **High-quality images** from Unsplash

### Data Generation Scripts
Located in the `scripts/` directory:
- `data_generator.py` - Core data generation logic
- `generate_data.py` - Main script for creating sample data
- `supabase_manager.py` - Database operations and management
- `upgrade_images.py` - Image quality management
- `config.py` - Configuration management

## Deployment

### Production Deployment Options

#### Option 1: Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

#### Option 2: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Option 3: Direct Server
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your values

# Start server
python main.py
```

### Environment Variables
Ensure all required environment variables are set in production:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Your Supabase service role key

### CORS Configuration
The backend is configured for:
- Development: `http://localhost:3000`
- Production: `https://dreamheaven.vercel.app`

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

### Sample API Calls
```bash
# Get all listings
curl "http://localhost:8000/listings"

# Search for properties in San Francisco
curl "http://localhost:8000/listings?location=San%20Francisco"

# Get listings with 3 bedrooms
curl "http://localhost:8000/listings?bedrooms=3"

# Search with AI
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{"query": "luxury apartments", "location": "New York"}'
```

## Maintenance

### Database Management
- Use Supabase dashboard for schema changes
- Scripts in `scripts/` directory for data operations
- Regular backups recommended

### Performance Optimization
- Database-level sorting for better performance
- Pagination to handle large datasets
- Efficient query patterns implemented

### Monitoring
- Health check endpoint for monitoring
- Debug endpoint for troubleshooting
- Comprehensive error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the API documentation at `/docs`
- Review the deployment checklist in `DEPLOYMENT_CHECKLIST.md`
- Check the health endpoint at `/health` 