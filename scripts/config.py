import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Dream Haven backend"""
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Data Generation Configuration
    NUM_HOSTS = int(os.getenv("NUM_HOSTS", "5"))
    NUM_LISTINGS = int(os.getenv("NUM_LISTINGS", "2000"))
    
    @classmethod
    def get_supabase_client(cls) -> Client:
        """Get Supabase client with service role key for admin operations"""
        if not cls.SUPABASE_URL or not cls.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        return create_client(cls.SUPABASE_URL, cls.SUPABASE_SERVICE_ROLE_KEY)
    
    @classmethod
    def get_supabase_anon_client(cls) -> Client:
        """Get Supabase client with anonymous key for regular operations"""
        if not cls.SUPABASE_URL or not cls.SUPABASE_ANON_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        return create_client(cls.SUPABASE_URL, cls.SUPABASE_ANON_KEY)
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY", 
            "SUPABASE_SERVICE_ROLE_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print("✅ Configuration validated successfully!")
        return True 