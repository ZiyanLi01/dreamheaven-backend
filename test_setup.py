#!/usr/bin/env python3
"""
Test script to verify Dream Haven Backend setup
"""

import sys
import os
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import supabase
        print("✅ Supabase imported successfully")
    except ImportError as e:
        print(f"❌ Supabase import failed: {e}")
        return False
    
    try:
        import faker
        print("✅ Faker imported successfully")
    except ImportError as e:
        print(f"❌ Faker import failed: {e}")
        return False
    
    try:
        from scripts.config import Config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Config module import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    load_dotenv()
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please copy env.example to .env and fill in your Supabase credentials")
        return False
    
    return True

def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        from scripts.config import Config
        from scripts.supabase_manager import SupabaseManager
        
        # Validate config
        Config.validate_config()
        
        # Test connection
        supabase = SupabaseManager()
        
        # Try to get a simple query
        result = supabase.client.table("profiles").select("id").limit(1).execute()
        print("✅ Supabase connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        print("Please check your Supabase credentials and ensure the database is set up")
        return False

def test_data_generator():
    """Test data generator"""
    print("\n🔍 Testing data generator...")
    
    try:
        from scripts.data_generator import RealEstateDataGenerator
        
        generator = RealEstateDataGenerator()
        
        # Test host generation
        host = generator.generate_host()
        if host and "email" in host and "first_name" in host:
            print("✅ Host generation working")
        else:
            print("❌ Host generation failed")
            return False
        
        # Test listing generation
        listing = generator.generate_listing(host["id"])
        if listing and "title" in listing and "price_per_night" in listing:
            print("✅ Listing generation working")
        else:
            print("❌ Listing generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data generator test failed: {e}")
        return False

def test_api_routes():
    """Test API route imports"""
    print("\n🔍 Testing API routes...")
    
    try:
        from api.routes import auth, buyers, listings, search
        print("✅ All API routes imported successfully")
        return True
    except Exception as e:
        print(f"❌ API routes import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏠 Dream Haven Backend Setup Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Supabase Connection", test_supabase_connection),
        ("Data Generator", test_data_generator),
        ("API Routes", test_api_routes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Dream Haven Backend is ready to go!")
        print("\nNext steps:")
        print("1. Run 'python scripts/generate_data.py' to create sample data")
        print("2. Run 'python main.py' to start the server")
        print("3. Visit http://localhost:8000/docs for API documentation")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main() 