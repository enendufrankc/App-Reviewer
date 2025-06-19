import os
import json
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

load_dotenv()

class AppConfig:
    def __init__(self):
        # Define project root first
        self.project_root = Path(__file__).parent.parent.parent
        
        # Supabase configuration - Fix the key mapping
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")  # For public operations
        self.supabase_key = os.environ.get("SUPABASE_KEY")  # This is the same as anon key
        self.supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        # TEMPORARY FIX: Use the working key (SUPABASE_KEY) instead of the broken service role key
        # The service role key in .env has a typo ("rose" instead of "role")
        if self.supabase_key:
            self.database_key = self.supabase_key
            print("Using SUPABASE_KEY for database operations (service key has typo)")
        elif self.supabase_anon_key:
            self.database_key = self.supabase_anon_key
            print("Using SUPABASE_ANON_KEY for database operations")
        elif self.supabase_service_key:
            self.database_key = self.supabase_service_key
            print("Using SUPABASE_SERVICE_ROLE_KEY for database operations")
        else:
            self.database_key = None
            print("⚠️  Warning: No Supabase key found")
        
        # Remove PostgreSQL connection logic since we're using Supabase client
        self.database_url = None  # Not needed for Supabase client
        print("✅ Using Supabase client for database operations")
        
        # Validate Supabase configuration
        if not self.supabase_url:
            print("⚠️  Warning: SUPABASE_URL not configured")
        if not self.database_key:
            print("⚠️  Warning: No valid Supabase key configured")
        
        if self.supabase_url and self.database_key:
            print("✅ Supabase configuration complete")
        
        self.service_account_file = 'credentials.json'
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        self.azure_openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.environ.get("AZURE_OPENAI_MODEL")
        self.ffmpeg_path = r"C:\Users\LENOVO\1. Projects\App Reviewer\ffmpeg\bin"
        
        # Database configuration
        self.encryption_key = os.environ.get("ENCRYPTION_KEY")
        
        # Batch processing configuration
        self.default_batch_size = int(os.environ.get("BATCH_SIZE", "10"))
        self.max_concurrent_files = int(os.environ.get("MAX_CONCURRENT_FILES", "3"))
        
        # Now you can use self.project_root
        self.templates_dir = self.project_root / "src" / "prompt_components" / "templates"
        self.criteria_file = self.templates_dir / "eligibility_criteria.txt"
        self.system_prompt_file = self.templates_dir / "system_prompt.txt"
        
        # Set FFmpeg path
        if os.path.exists(self.ffmpeg_path):
            os.environ["PATH"] = self.ffmpeg_path + os.pathsep + os.environ["PATH"]
        
        # Validation
        if not self.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        if not self.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        if not self.deployment_name:
            raise ValueError("AZURE_OPENAI_MODEL environment variable is required")
    
    def get_supabase_client(self) -> Client:
        """Get Supabase client instance"""
        options = ClientOptions(function_client_timeout = 15)
        return create_client(self.supabase_url, self.database_key, options=options)

def get_user_eligibility_criteria(user_id: str = None) -> str:
    """
    Get eligibility criteria - from database if user_id provided, otherwise fallback to file
    """
    if user_id:
        # This will be implemented to fetch from database
        # For now, return default criteria
        return safe_load_prompt(config.criteria_file)
    else:
        return safe_load_prompt(config.criteria_file)

def get_json_schema() -> str:
    try:
        from src.models.evaluation_models import CandidateReview
        schema = CandidateReview.model_json_schema()
        return json.dumps(schema, indent=2)
    except Exception as e:
        raise Exception(f"Error generating JSON schema: {str(e)}")

# Initialize config
config = AppConfig()

# Load prompts with proper error handling
def safe_load_prompt(file_path):
    try:
        from src.prompt_components.prompt_loader import load_prompt
        return load_prompt(file_path)
    except Exception as e:
        print(f"Warning: Could not load prompt from {file_path}: {e}")
        return ""

# Default criteria (fallback)
ELIGIBILITY_CRITERIA = safe_load_prompt(config.criteria_file)
SYSTEM_PROMPT_TEMPLATE = safe_load_prompt(config.system_prompt_file)
REVIEW_SCHEMA = get_json_schema()

# Dynamic system prompt
def get_system_prompt(user_id: str = None) -> str:
    """Get system prompt with user-specific criteria"""
    criteria = get_user_eligibility_criteria(user_id)
    return SYSTEM_PROMPT_TEMPLATE.replace("{schema}", REVIEW_SCHEMA)

SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.replace("{schema}", REVIEW_SCHEMA)