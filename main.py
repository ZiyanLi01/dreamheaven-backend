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

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(buyers.router, prefix="/api/buyers", tags=["Buyers"])
app.include_router(listings.router, prefix="/api/listings", tags=["Listings"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])

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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 