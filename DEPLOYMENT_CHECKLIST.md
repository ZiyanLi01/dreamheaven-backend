# Dream Haven Backend - Deployment Checklist

## Pre-Deployment Cleanup Completed

### Files Removed:
- All test files (`test_*.py`)
- Data generation scripts (moved to scripts/ directory)
- Database migration scripts (one-time use)
- Documentation files for development
- Large data files (`house_images_*.json`)
- `__pycache__` directories

### Files Kept:
- `main.py` - FastAPI application entry point
- `api/` - Core API routes and logic
- `scripts/` - Data management utilities (useful for maintenance)
- `requirements.txt` - Production dependencies
- `env.example` - Environment configuration template
- `start.sh` - Production startup script
- `README.md` - Documentation
- `.gitignore` - Git ignore rules

## Production Configuration

### Environment Variables Required:
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

### CORS Configuration:
- Configured for `http://localhost:3000` (development)
- Configured for `https://dreamheaven.vercel.app` (production)

## Deployment Options

### Option 1: Railway (Recommended)
1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Option 2: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 3: Direct Server
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your values

# Start server
python main.py
```

## API Endpoints

### Core Endpoints:
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /debug` - Debug information

### Authentication:
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Listings:
- `GET /listings` - Get all listings with filters
- `GET /listings/{id}` - Get specific listing

### Search:
- `GET /search` - Search listings with query parameters
- `POST /search/` - AI-powered search with filters

### Buyers:
- `GET /buyers` - Get buyer information
- `POST /buyers` - Create buyer profile

## Health Check Endpoints

Test these endpoints after deployment:
```bash
# Basic health check
curl https://your-domain.com/health

# Debug information
curl https://your-domain.com/debug

# Test listings endpoint
curl https://your-domain.com/listings

# Test search endpoint
curl https://your-domain.com/search
```

## Post-Deployment Tasks

1. **Verify Environment Variables**: Ensure all Supabase credentials are set
2. **Test Database Connection**: Check `/debug` endpoint
3. **Test CORS**: Verify frontend can connect
4. **Monitor Logs**: Check for any errors
5. **Performance Test**: Test search and listing endpoints with real data

## Maintenance Scripts

The `scripts/` directory contains utilities for:
- Data generation (`data_generator.py`)
- Database management (`supabase_manager.py`)
- Image management (`upgrade_images.py`)
- Configuration management (`config.py`)

These are useful for ongoing maintenance and data updates.

## Ready for Deployment!

Your backend is now clean and ready for production deployment.
