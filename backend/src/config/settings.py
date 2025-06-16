import os
import json
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class AppConfig:
    def __init__(self):
        # Define project root first
        self.project_root = Path(__file__).parent.parent.parent
        
        self.service_account_file = 'credentials.json'
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        self.azure_openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.environ.get("AZURE_OPENAI_MODEL")
        self.ffmpeg_path = r"C:\Users\LENOVO\1. Projects\App Reviewer\ffmpeg\bin"
        
        # Now you can use self.project_root
        self.templates_dir = self.project_root / "src" / "prompt_components" / "templates"
        self.criteria_file = self.templates_dir / "eligibility_criteria.txt"
        self.system_prompt_file = self.templates_dir / "system_prompt.txt"
        
        # Set FFmpeg path
        os.environ["PATH"] = self.ffmpeg_path + os.pathsep + os.environ["PATH"]
        
        # Validation
        if not self.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        if not self.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        if not self.deployment_name:
            raise ValueError("AZURE_OPENAI_MODEL environment variable is required")

def reload_eligibility_criteria():
    """
    Reload eligibility criteria from file
    """
    global ELIGIBILITY_CRITERIA
    criteria_path = "src/prompt_components/templates/eligibility_criteria.txt"
    
    try:
        with open(criteria_path, 'r', encoding='utf-8') as file:
            ELIGIBILITY_CRITERIA = file.read().strip()
    except Exception as e:
        print(f"Warning: Could not reload eligibility criteria: {e}")


def get_json_schema() -> str:
    try:
        # You have CandidateReview in both locations, use the prompt_components one
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

ELIGIBILITY_CRITERIA = safe_load_prompt(config.criteria_file)
SYSTEM_PROMPT_TEMPLATE = safe_load_prompt(config.system_prompt_file)
REVIEW_SCHEMA = get_json_schema()

# Fix the variable name (was 'system_prompt', should be 'SYSTEM_PROMPT_TEMPLATE')
SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.replace("{schema}", REVIEW_SCHEMA)