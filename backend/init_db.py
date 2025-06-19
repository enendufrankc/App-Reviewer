import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_direct_connection():
    """Test direct Supabase connection first"""
    print("Testing direct Supabase connection...")
    
    try:
        from supabase import create_client
        from supabase.lib.client_options import ClientOptions
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        print(f"SUPABASE_URL: {'✅ Set' if url else '❌ Missing'}")
        print(f"SUPABASE_KEY: {'✅ Set' if key else '❌ Missing'}")
        
        if not url or not key:
            print("❌ Missing SUPABASE_URL or SUPABASE_KEY")
            return False
        
        options = ClientOptions(function_client_timeout=15)
        client = create_client(url, key, options)
        
        # Test connection
        result = client.table("candidate_evaluations").select("*").limit(1).execute()
        print("✅ Direct Supabase connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Direct connection failed: {str(e)}")
        return False

async def init_database():
    """Initialize database tables"""
    try:
        print("=== Database Initialization ===")
        
        # First test direct connection
        if not await test_direct_connection():
            print("❌ Cannot establish direct connection. Check your environment variables.")
            return
        
        print("\nLoading application configuration...")
        from src.config.settings import AppConfig
        config = AppConfig()
        
        print("Creating database service...")
        from src.services.database_service import DatabaseService
        db_service = DatabaseService(config)
        
        if not db_service.is_available():
            print("❌ Database service not available - check your configuration")
            return
        
        print("Testing database service connection...")
        if not await db_service.test_connection():
            print("❌ Database service connection failed")
            return
        
        print("✅ Database service connection successful!")
        
        print("Creating/verifying database tables...")
        await db_service.create_tables()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(init_database())
