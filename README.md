# Dream Haven Backend 🏠

A modern FastAPI backend for the Dream Haven real estate platform, featuring AI-powered search capabilities and comprehensive property management.

## 🚀 Features

- **FastAPI Backend**: High-performance REST API with automatic documentation
- **Supabase Integration**: PostgreSQL database with real-time capabilities
- **Data Generation**: Automated creation of realistic real estate data
- **Authentication**: Complete user authentication and authorization system
- **Search API**: Advanced search with filters, sorting, and geolocation
- **AI-Ready**: Prepared for RAG (Retrieval-Augmented Generation) integration

## 📁 Project Structure

```
dreamheaven-backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── README.md              # This file
├── scripts/               # Data generation scripts
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── data_generator.py  # Real estate data generation
│   ├── supabase_manager.py # Database operations
│   └── generate_data.py   # Main data generation script
├── api/                   # API routes
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py        # Authentication endpoints
│       ├── users.py       # User management
│       ├── listings.py    # Property listings CRUD
│       └── search.py      # Search functionality
└── data/                  # Generated data backups
```

## 🛠️ Setup Instructions

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
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

### 4. Database Setup

Create the following tables in your Supabase database:

#### Profiles Table
```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    phone TEXT,
    avatar_url TEXT,
    bio TEXT,
    is_host BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Listings Table
```sql
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id UUID REFERENCES profiles(id),
    title TEXT NOT NULL,
    description TEXT,
    property_type TEXT,
    bedrooms INTEGER,
    bathrooms INTEGER,
    max_guests INTEGER,
    square_feet INTEGER,
    price_per_night DECIMAL(10,2),
    price_per_month DECIMAL(10,2),
    city TEXT,
    state TEXT,
    country TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    address TEXT,
    neighborhood TEXT,
    amenities TEXT[],
    images TEXT[],
    is_available BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3,2) DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

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
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Authentication (`/api/auth`)
- `POST /login` - User login
- `POST /register` - User registration
- `POST /logout` - User logout
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user
- `POST /forgot-password` - Send password reset email
- `POST /reset-password` - Reset password
- `POST /change-password` - Change password
- `POST /verify-email` - Verify email address

### Users (`/api/users`)
- `GET /` - Get all users
- `GET /{user_id}` - Get specific user
- `GET /email/{email}` - Get user by email
- `POST /` - Create user
- `PUT /{user_id}` - Update user
- `DELETE /{user_id}` - Delete user
- `GET /hosts/list` - Get all hosts
- `GET /verified/list` - Get verified users
- `PUT /{user_id}/verify` - Verify user
- `PUT /{user_id}/unverify` - Unverify user

### Listings (`/api/listings`)
- `GET /` - Get all listings with filters
- `GET /{listing_id}` - Get specific listing
- `POST /` - Create listing
- `PUT /{listing_id}` - Update listing
- `DELETE /{listing_id}` - Delete listing
- `GET /host/{host_id}` - Get listings by host
- `GET /cities/list` - Get all cities
- `GET /types/list` - Get all property types

### Search (`/api/search`)
- `GET /` - Search listings with filters
- `GET /nearby` - Search listings by location
- `GET /suggestions` - Get search suggestions
- `GET /stats` - Get search statistics
- `POST /ai-search` - AI-powered search (coming soon)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Required |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Required |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `NUM_HOSTS` | Number of hosts to generate | `5` |
| `NUM_LISTINGS` | Number of listings to generate | `2000` |

### Data Generation Configuration

The data generator creates realistic real estate data including:
- **10 Major US Cities**: San Francisco, New York, Los Angeles, Chicago, Miami, Seattle, Austin, Denver, Portland, Nashville
- **10 Property Types**: Apartment, House, Condo, Townhouse, Villa, Studio, Loft, Penthouse, Duplex, Cottage
- **21 Amenities**: WiFi, Air Conditioning, Heating, Kitchen, Washing Machine, Dryer, Dishwasher, Parking, Gym, Pool, Garden, Balcony, Fireplace, Elevator, Doorman, Security System, Pet Friendly, Furnished, Mountain View, Ocean View, City View

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Test specific endpoint
curl http://localhost:8000/health
```

## 🚀 Deployment

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔮 Future Features

- **RAG Integration**: AI-powered natural language search
- **Real-time Updates**: WebSocket support for live updates
- **Image Upload**: Property image management
- **Booking System**: Reservation and payment processing
- **Reviews & Ratings**: User review system
- **Analytics**: Property performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the Supabase documentation

---

**Dream Haven Backend** - Building the future of real estate search 🏠✨ 