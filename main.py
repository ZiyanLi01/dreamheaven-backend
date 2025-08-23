from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routers
from api.routes import listings, buyers, auth, search

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Dream Haven Backend starting up...")
    yield
    # Shutdown
    print("🛑 Dream Haven Backend shutting down...")

app = FastAPI(
    title="Dream Haven Backend",
    description="Real estate platform backend with AI-powered search",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://dreamheaven.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers without /api prefix for cleaner URLs
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(buyers.router, prefix="/buyers", tags=["Buyers"])
app.include_router(listings.router, prefix="/listings", tags=["Listings"])
app.include_router(search.router, prefix="/search", tags=["Search"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Dream Haven Backend! 🏠",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dream-haven-backend"}

@app.get("/debug")
async def debug_request():
    """Debug endpoint to help identify frontend request issues"""
    from datetime import datetime
    from scripts.supabase_manager import SupabaseManager
    
    try:
        # Test Supabase connection
        supabase = SupabaseManager()
        test_result = supabase.client.table("listings_v2").select("id").limit(1).execute()
        supabase_status = "connected" if test_result.data else "no_data"
    except Exception as e:
        supabase_status = f"error: {str(e)}"
    
    return {
        "status": "debug_info",
        "supabase_status": supabase_status,
        "server_time": datetime.now().isoformat(),
        "message": "Backend is running and ready to handle requests"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    ) 