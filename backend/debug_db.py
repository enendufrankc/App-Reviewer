import os
import sys
import socket
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_keys():
    """Test which Supabase keys are available"""
    print("=== Supabase Keys Test ===")
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    print(f"SUPABASE_ANON_KEY: {'✅ Set' if supabase_anon_key else '❌ Missing'}")
    print(f"SUPABASE_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if supabase_service_key else '❌ Missing'}")
    
    if supabase_url:
        print(f"Supabase URL: {supabase_url}")
    
    # Check if keys are the same
    if supabase_key and supabase_anon_key:
        if supabase_key == supabase_anon_key:
            print("ℹ️  SUPABASE_KEY and SUPABASE_ANON_KEY are identical")
        else:
            print("⚠️  SUPABASE_KEY and SUPABASE_ANON_KEY are different")
    
    # Test each key
    keys_to_test = []
    if supabase_service_key:
        keys_to_test.append(("SERVICE_ROLE_KEY", supabase_service_key))
    if supabase_key:
        keys_to_test.append(("SUPABASE_KEY", supabase_key))
    if supabase_anon_key:
        keys_to_test.append(("ANON_KEY", supabase_anon_key))
    
    return supabase_url, keys_to_test

def test_supabase_direct_connection():
    """Test direct Supabase connection like in your working notebook"""
    print("\n=== Direct Supabase Connection Test ===")
    
    try:
        from supabase import create_client
        from supabase.lib.client_options import ClientOptions
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")  # Use the same key as in your working test
        
        if not url or not key:
            print("❌ Missing SUPABASE_URL or SUPABASE_KEY")
            return False
        
        print(f"Testing connection with SUPABASE_KEY...")
        options = ClientOptions(function_client_timeout=15)
        client = create_client(url, key, options)
        
        # Test the exact same query as your working notebook
        result = client.table("candidate_evaluations").select("*").execute()
        print(f"✅ Direct connection successful! Found {len(result.data)} candidate evaluations")
        
        # Test other tables
        try:
            users_result = client.table("users").select("*").execute()
            print(f"✅ Users table accessible: {len(users_result.data)} records")
        except Exception as e:
            print(f"⚠️  Users table: {str(e)}")
        
        try:
            sessions_result = client.table("evaluation_sessions").select("*").execute()
            print(f"✅ Sessions table accessible: {len(sessions_result.data)} records")
        except Exception as e:
            print(f"⚠️  Sessions table: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct connection failed: {str(e)}")
        return False

def test_network_connectivity():
    """Test basic network connectivity to Google and Supabase"""
    print("\n=== Network Connectivity Test ===")
    
    # Test Google (basic internet)
    try:
        socket.gethostbyname("google.com")
        print("✅ Internet connectivity: OK")
        internet_ok = True
    except socket.gaierror:
        print("❌ Internet connectivity: FAILED")
        internet_ok = False
    
    # Test Supabase general domain
    try:
        socket.gethostbyname("supabase.co")
        print("✅ Supabase domain reachable: OK")
        supabase_ok = True
    except socket.gaierror:
        print("❌ Supabase domain reachable: FAILED")
        supabase_ok = False
    
    # Test specific Supabase project domain
    supabase_url = os.environ.get("SUPABASE_URL")
    if supabase_url:
        api_host = supabase_url.replace("https://", "").replace("http://", "")
        try:
            ip = socket.gethostbyname(api_host)
            print(f"✅ Project domain reachable: {api_host} -> {ip}")
            project_ok = True
        except socket.gaierror as e:
            print(f"❌ Project domain unreachable: {api_host} - {e}")
            project_ok = False
    else:
        project_ok = False
    
    return internet_ok and supabase_ok and project_ok

async def test_database_service():
    """Test the database service"""
    print("\n=== Database Service Test ===")
    
    try:
        # Add the current directory to the Python path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from src.config.settings import AppConfig
        from src.services.database_service import DatabaseService
        
        config = AppConfig()
        db_service = DatabaseService(config)
        
        if not db_service.is_available():
            print("❌ Database service not available")
            return False
        
        print("🔄 Testing database service connection...")
        connection_ok = await db_service.test_connection()
        
        if connection_ok:
            print("✅ Database service connection successful!")
            return True
        else:
            print("❌ Database service connection failed")
            return False
    
    except Exception as e:
        print(f"❌ Database service test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Enhanced Database Connection Debug ===")
    
    # Test basic network connectivity
    network_ok = test_network_connectivity()
    
    # Test Supabase keys configuration
    supabase_url, keys_to_test = test_supabase_keys()
    
    if network_ok and supabase_url and keys_to_test:
        # Test direct connection (like your working notebook)
        direct_ok = test_supabase_direct_connection()
        
        if direct_ok:
            print("\n🔄 Direct connection works! Testing database service...")
            asyncio.run(test_database_service())
        else:
            print("\n❌ Direct connection failed. Check your API keys.")
    else:
        print("\n❌ Basic tests failed. Fix these issues first:")
        if not network_ok:
            print("  • Check your internet connection")
        if not supabase_url:
            print("  • Check SUPABASE_URL in your .env file")
        if not keys_to_test:
            print("  • Check your Supabase API keys in .env file")
