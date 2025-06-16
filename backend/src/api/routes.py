import io
import json
import base64
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse

import shutil
from datetime import datetime
from pathlib import Path

from src.models.candidate_models import CandidateEvaluationRequest, CandidateEvaluationResponse
from src.models.evaluation_models import EligibilityCriteriaUpdate, EligibilityCriteriaValidation
from src.config.settings import AppConfig
from src.services.drive_service import GoogleDriveService
from src.services.file_processor import FileProcessor
from src.services.ai_service import AIEvaluationService
from src.services.candidate_processor import CandidateProcessor

# Initialize services
config = AppConfig()
drive_service = GoogleDriveService(config)
file_processor = FileProcessor()
ai_service = AIEvaluationService(config)
processor = CandidateProcessor(drive_service, file_processor, ai_service)

router = APIRouter()

@router.post("/evaluate-candidates", response_model=CandidateEvaluationResponse)
async def evaluate_candidates(file: UploadFile = File(...)):
    """
    Upload a CSV file containing candidate data and get comprehensive evaluations
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read CSV file
        contents = await file.read()
        
        # Try multiple encoding methods
        csv_content = None
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                csv_content = contents.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if csv_content is None:
            raise HTTPException(
                status_code=400, 
                detail="Unable to decode file. Please ensure the CSV file uses UTF-8, Latin-1, or Windows-1252 encoding"
            )
        
        # Convert to DataFrame with error handling
        try:
            data = pd.read_csv(io.StringIO(csv_content), encoding_errors='ignore')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing CSV file: {str(e)}")
        
        # Validate DataFrame is not empty
        if data.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty or contains no valid data")
        
        # Validate required columns
        required_columns = ['Email address']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            available_columns = list(data.columns)
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}. Available columns: {available_columns}"
            )
        
        # Check for valid email addresses
        valid_emails = data['Email address'].dropna()
        if len(valid_emails) == 0:
            raise HTTPException(status_code=400, detail="No valid email addresses found in the CSV file")
        
        # Process all candidates
        results = await processor.process_all_candidates(data)
        
        # Generate summary
        accepted = sum(1 for r in results if r.get('outcome') == 'Accepted')
        rejected = sum(1 for r in results if r.get('outcome') == 'Rejected')
        errors = sum(1 for r in results if 'error' in r)
        
        summary = {
            "total_processed": len(results),
            "accepted": accepted,
            "rejected": rejected,
            "errors": errors
        }
        
        return CandidateEvaluationResponse(
            status="success",
            message=f"Successfully processed {len(results)} candidates",
            results=results,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")



@router.post("/evaluate-candidates-from-path")
async def evaluate_candidates_from_path(csv_path: str):
    """
    Process candidates from a CSV file path (for local testing)
    """
    try:
        # Read CSV file
        data = pd.read_csv(csv_path, encoding='utf-8', encoding_errors='ignore')
        
        # Validate required columns
        required_columns = ['Email address']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process all candidates
        results = await processor.process_all_candidates(data)
        
        # Generate summary
        accepted = sum(1 for r in results if r.get('outcome') == 'Accepted')
        rejected = sum(1 for r in results if r.get('outcome') == 'Rejected')
        errors = sum(1 for r in results if 'error' in r)
        
        summary = {
            "total_processed": len(results),
            "accepted": accepted,
            "rejected": rejected,
            "errors": errors
        }
        
        return {
            "status": "success",
            "message": f"Successfully processed {len(results)} candidates",
            "results": results,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy", 
        "message": "App Reviewer Backend is running",
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
    }

@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy", 
        "message": "App Reviewer API is running",
        "version": "1.0.0"
    }

@router.get("/eligibility-criteria")
async def get_eligibility_criteria():
    """
    Get the current eligibility criteria content
    """
    try:
        criteria_file_path = "src/prompt_components/templates/eligibility_criteria.txt"
        
        with open(criteria_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return {
            "status": "success",
            "content": content,
            "message": "Eligibility criteria retrieved successfully"
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Eligibility criteria file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading eligibility criteria: {str(e)}")


@router.put("/eligibility-criteria")
async def update_eligibility_criteria(request: EligibilityCriteriaUpdate):
    """
    Update the eligibility criteria content
    """
    try:
        criteria_file_path = "src/prompt_components/templates/eligibility_criteria.txt"
        
        # Validate that content is not empty (use request.content, not criteria_content)
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="Eligibility criteria content cannot be empty")
        
        # Create backup of current file
        backup_path = f"src/prompt_components/templates/eligibility_criteria_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        shutil.copy2(criteria_file_path, backup_path)
        
        # Write new content (use request.content, not criteria_content)
        with open(criteria_file_path, 'w', encoding='utf-8') as file:
            file.write(request.content)
        
        # Update the config module to reload the criteria
        from src.config.settings import reload_eligibility_criteria
        reload_eligibility_criteria()
        
        return {
            "status": "success",
            "message": "Eligibility criteria updated successfully",
            "backup_created": backup_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating eligibility criteria: {str(e)}")


@router.post("/eligibility-criteria/validate")
async def validate_eligibility_criteria(request: EligibilityCriteriaValidation):
    """
    Validate eligibility criteria content without saving
    """
    try:
        # Use request.content instead of criteria_content
        criteria_content = request.content
        
        # Basic validation checks
        if not criteria_content.strip():
            return {
                "valid": False,
                "message": "Content cannot be empty"
            }
        
        # Check for basic structure
        lines = criteria_content.strip().split('\n')
        if len(lines) < 2:
            return {
                "valid": False,
                "message": "Criteria should have at least a title and one criterion"
            }
        
        # Check for arrow indicators (→) which seem to be the format
        criteria_lines = [line for line in lines if '→' in line]
        if len(criteria_lines) == 0:
            return {
                "valid": False,
                "message": "No criteria found. Use '→' to indicate criteria items"
            }
        
        return {
            "valid": True,
            "message": f"Valid criteria format with {len(criteria_lines)} criteria items",
            "preview": criteria_content[:200] + "..." if len(criteria_content) > 200 else criteria_content
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }

@router.get("/credentials")
async def get_credentials_info():
    """
    Get information about the current credentials file (without exposing sensitive data)
    """
    try:
        credentials_path = Path("credentials.json")
        
        if not credentials_path.exists():
            raise HTTPException(status_code=404, detail="Credentials file not found")
        
        # Read and parse credentials to get non-sensitive info
        with open(credentials_path, 'r', encoding='utf-8') as file:
            creds_data = json.load(file)
        
        # Return only non-sensitive information
        safe_info = {
            "type": creds_data.get("type"),
            "project_id": creds_data.get("project_id"),
            "client_email": creds_data.get("client_email"),
            "client_id": creds_data.get("client_id"),
            "auth_uri": creds_data.get("auth_uri"),
            "token_uri": creds_data.get("token_uri"),
            "universe_domain": creds_data.get("universe_domain", "googleapis.com"),
            "file_size": credentials_path.stat().st_size,
            "last_modified": datetime.fromtimestamp(credentials_path.stat().st_mtime).isoformat()
        }
        
        return {
            "status": "success",
            "message": "Credentials information retrieved successfully",
            "credentials_info": safe_info
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in credentials file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading credentials: {str(e)}")

@router.post("/credentials/upload")
async def upload_credentials(file: UploadFile = File(...)):
    """
    Upload a new credentials.json file to replace the existing one
    """
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read and validate the uploaded file
        contents = await file.read()
        
        try:
            # Parse JSON to validate format
            creds_data = json.loads(contents.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File encoding error. Please use UTF-8 encoding")
        
        # Validate that it's a valid Google Service Account credential
        required_fields = [
            "type", "project_id", "private_key_id", "private_key", 
            "client_email", "client_id", "auth_uri", "token_uri"
        ]
        
        missing_fields = [field for field in required_fields if field not in creds_data]
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid credentials format. Missing required fields: {missing_fields}"
            )
        
        if creds_data.get("type") != "service_account":
            raise HTTPException(
                status_code=400, 
                detail="Invalid credential type. Only 'service_account' credentials are supported"
            )
        
        # Create backup of existing credentials file
        credentials_path = Path("credentials.json")
        backup_created = False
        backup_path = None
        
        if credentials_path.exists():
            backup_path = f"credentials_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(credentials_path, backup_path)
            backup_created = True
        
        # Write new credentials file
        with open(credentials_path, 'w', encoding='utf-8') as f:
            json.dump(creds_data, f, indent=2)
        
        # Extract safe information for response
        safe_info = {
            "type": creds_data.get("type"),
            "project_id": creds_data.get("project_id"),
            "client_email": creds_data.get("client_email"),
            "client_id": creds_data.get("client_id")
        }
        
        response_data = {
            "status": "success",
            "message": "Credentials file uploaded and replaced successfully",
            "credentials_info": safe_info
        }
        
        if backup_created:
            response_data["backup_created"] = backup_path
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading credentials: {str(e)}")

@router.post("/credentials/validate")
async def validate_credentials(file: UploadFile = File(...)):
    """
    Validate a credentials file without saving it
    """
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            return {
                "valid": False,
                "message": "Only JSON files are supported"
            }
        
        # Read and validate the uploaded file
        contents = await file.read()
        
        try:
            # Parse JSON to validate format
            creds_data = json.loads(contents.decode('utf-8'))
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "message": f"Invalid JSON format: {str(e)}"
            }
        except UnicodeDecodeError:
            return {
                "valid": False,
                "message": "File encoding error. Please use UTF-8 encoding"
            }
        
        # Validate that it's a valid Google Service Account credential
        required_fields = [
            "type", "project_id", "private_key_id", "private_key", 
            "client_email", "client_id", "auth_uri", "token_uri"
        ]
        
        missing_fields = [field for field in required_fields if field not in creds_data]
        if missing_fields:
            return {
                "valid": False,
                "message": f"Missing required fields: {missing_fields}"
            }
        
        if creds_data.get("type") != "service_account":
            return {
                "valid": False,
                "message": "Invalid credential type. Only 'service_account' credentials are supported"
            }
        
        # Additional validations
        if not creds_data.get("private_key", "").startswith("-----BEGIN PRIVATE KEY-----"):
            return {
                "valid": False,
                "message": "Invalid private key format"
            }
        
        if "@" not in creds_data.get("client_email", ""):
            return {
                "valid": False,
                "message": "Invalid client email format"
            }
        
        # Extract safe information for preview
        safe_info = {
            "type": creds_data.get("type"),
            "project_id": creds_data.get("project_id"),
            "client_email": creds_data.get("client_email"),
            "client_id": creds_data.get("client_id"),
            "universe_domain": creds_data.get("universe_domain", "googleapis.com")
        }
        
        return {
            "valid": True,
            "message": "Valid Google Service Account credentials",
            "preview": safe_info
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }

@router.delete("/credentials")
async def delete_credentials():
    """
    Delete the current credentials file (creates backup first)
    """
    try:
        credentials_path = Path("credentials.json")
        
        if not credentials_path.exists():
            raise HTTPException(status_code=404, detail="Credentials file not found")
        
        # Create backup before deletion
        backup_path = f"credentials_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(credentials_path, backup_path)
        
        # Delete the original file
        credentials_path.unlink()
        
        return {
            "status": "success",
            "message": "Credentials file deleted successfully",
            "backup_created": backup_path
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting credentials: {str(e)}")

@router.post("/credentials/test")
async def test_credentials():
    """
    Test the current credentials by attempting to authenticate with Google Drive API
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials_path = Path("credentials.json")
        
        if not credentials_path.exists():
            raise HTTPException(status_code=404, detail="Credentials file not found")
        
        # Test authentication
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path), 
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        # Try to build the service
        service = build('drive', 'v3', credentials=credentials)
        
        # Test with a simple API call
        about = service.about().get(fields="user").execute()
        
        return {
            "status": "success",
            "message": "Credentials authentication successful",
            "service_account_email": about.get("user", {}).get("emailAddress", "Unknown")
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Credentials file not found")
    except Exception as e:
        return {
            "status": "error",
            "message": f"Authentication failed: {str(e)}"
        }