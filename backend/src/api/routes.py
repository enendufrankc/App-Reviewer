import io
import json
import base64
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Form, Request
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
from src.services.database_service import DatabaseService


# Initialize services
config = AppConfig()
drive_service = GoogleDriveService(config)
file_processor = FileProcessor()
ai_service = AIEvaluationService(config)
processor = CandidateProcessor(drive_service, file_processor, ai_service)
db_service = DatabaseService(config)


router = APIRouter()

@router.post("/evaluate-candidates", response_model=CandidateEvaluationResponse)
async def evaluate_candidates(
    request: Request,
    file: UploadFile = File(...),
    user_email: str = Form(...),  # This is the LOGGED-IN USER email, not candidate email
    session_name: str = Form(None)
):
    """
    Upload a CSV file containing candidate data and get comprehensive evaluations
    
    Args:
        file: CSV file containing candidate data with 'Email address' column
        user_email: Email of the LOGGED-IN USER (for session management)
        session_name: Optional session name for this evaluation batch
    
    Note: 
        - user_email is the logged-in user (e.g., admin@lbs.edu.ng)
        - CSV contains candidate emails (e.g., candidate1@example.com, candidate2@example.com)
        - These are completely different and should never be confused!
    """
    try:
        print(f"🔍 === EVALUATION REQUEST DEBUG ===")
        print(f"📧 LOGGED-IN USER: {user_email}")
        print(f"📁 File: {file.filename}")
        print(f"📋 Session: {session_name}")
        
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Validate LOGGED-IN USER email
        if not user_email or user_email.strip() == "":
            raise HTTPException(
                status_code=400, 
                detail="Logged-in user email is required. Please log in and try again."
            )
        
        if "@" not in user_email or "." not in user_email:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid logged-in user email format: '{user_email}'"
            )
        
        print(f"✅ LOGGED-IN USER VALIDATED: {user_email}")
        
        # Create user session for the LOGGED-IN USER
        logged_in_user_id = None
        session_id = None
        
        if not session_name:
            session_name = f"Evaluation Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        print(f"🔧 Creating session for LOGGED-IN USER: {user_email}")
        
        if db_service.is_available():
            try:
                # Create/get the LOGGED-IN USER record
                logged_in_user = await db_service.create_or_get_user(user_email)
                logged_in_user_id = logged_in_user["id"]
                print(f"✅ LOGGED-IN USER record: {logged_in_user_id}")
                
                # Create evaluation session for the LOGGED-IN USER
                session_id = await db_service.create_evaluation_session(logged_in_user_id, session_name)
                print(f"✅ Created session {session_id} for LOGGED-IN USER {user_email}")
            except Exception as e:
                print(f"⚠️  Database session creation failed: {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to create user session. Please try again."
                )
        else:
            raise HTTPException(
                status_code=503, 
                detail="Database service unavailable."
            )
        
        # Process CSV file to extract CANDIDATE data
        contents = await file.read()
        csv_content = None
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                csv_content = contents.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if csv_content is None:
            raise HTTPException(status_code=400, detail="Unable to decode CSV file")
        
        # Parse CSV to get CANDIDATE data
        try:
            candidate_data = pd.read_csv(io.StringIO(csv_content), encoding_errors='ignore')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
        
        if candidate_data.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Validate CSV has candidate email column
        required_columns = ['Email address']
        missing_columns = [col for col in required_columns if col not in candidate_data.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"CSV missing required columns: {missing_columns}"
            )
        
        # Extract CANDIDATE emails from CSV
        candidate_emails = candidate_data['Email address'].dropna().tolist()
        if len(candidate_emails) == 0:
            raise HTTPException(status_code=400, detail="No candidate email addresses found in CSV")
        
        print(f"📊 Found {len(candidate_emails)} CANDIDATES to evaluate")
        print(f"📧 First few candidate emails: {candidate_emails[:3]}")
        print(f"🔒 All evaluations will be saved under LOGGED-IN USER: {user_email}")
        
        # Update session with candidate count
        if session_id and db_service.is_available():
            await db_service.update_session_progress(
                session_id, 
                total_candidates=len(candidate_emails)
            )
        
        # Process candidates using LOGGED-IN USER context
        print(f"🔄 Processing candidates with LOGGED-IN USER context: {logged_in_user_id}")
        results = await processor.process_all_candidates(
            candidate_data, 
            logged_in_user_id,  # Use logged-in user ID for criteria/permissions
            db_service
        )
        
        # Save results to database under the LOGGED-IN USER's session
        saved_count = 0
        if session_id and db_service.is_available():
            print(f"💾 Saving {len(results)} evaluations to LOGGED-IN USER's session")
            
            for i, result in enumerate(results):
                candidate_email = result.get('email', 'Unknown')
                print(f"💾 Saving evaluation {i+1}/{len(results)}: {candidate_email}")
                
                if not result.get('error'):
                    try:
                        db_result = processor._convert_to_db_format(result)
                        candidate_id = await db_service.save_candidate_evaluation(session_id, db_result)
                        saved_count += 1
                        print(f"✅ Saved candidate evaluation: {candidate_email}")
                    except Exception as e:
                        print(f"❌ Failed to save evaluation for {candidate_email}: {str(e)}")
        
        print(f"💾 SUMMARY: Processed {len(results)} candidates, saved {saved_count} evaluations")
        print(f"🔒 All data belongs to LOGGED-IN USER: {user_email}")
        
        # Generate summary
        accepted = sum(1 for r in results if r.get('outcome') == 'Accepted')
        rejected = sum(1 for r in results if r.get('outcome') == 'Rejected')
        errors = sum(1 for r in results if 'error' in r)
        
        summary = {
            "total_processed": len(results),
            "accepted": accepted,
            "rejected": rejected,
            "errors": errors,
            "saved_to_database": saved_count
        }
        
        # Complete session
        if session_id and db_service.is_available():
            await db_service.complete_session(session_id, summary)
        
        return CandidateEvaluationResponse(
            status="success",
            message=f"Successfully processed {len(results)} candidates for user {user_email}",
            results=results,
            summary=summary,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.post("/evaluate-candidates-v2", response_model=CandidateEvaluationResponse)
async def evaluate_candidates_v2(request: Request):
    """
    Alternative implementation with manual form parsing
    """
    try:
        print(f"🔍 === MANUAL FORM PARSING DEBUG ===")
        
        # Parse form data manually
        form_data = await request.form()
        
        print(f"📋 Received form fields:")
        for key, value in form_data.items():
            if hasattr(value, 'filename'):  # It's a file
                print(f"  - {key}: File({value.filename}, {value.content_type})")
            else:
                print(f"  - {key}: '{value}'")
        
        # Extract file
        if 'file' not in form_data:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        file = form_data['file']
        if not hasattr(file, 'filename'):
            raise HTTPException(status_code=400, detail="Invalid file upload")
        
        # Extract form parameters
        user_email = form_data.get('user_email', '')
        session_name = form_data.get('session_name', '')
        
        print(f"📧 Extracted parameters:")
        print(f"  - user_email: '{user_email}'")
        print(f"  - session_name: '{session_name}'")
        
        # Validate
        if not user_email or str(user_email).strip() == '':
            raise HTTPException(
                status_code=400, 
                detail="User email is required. Please log in and try again."
            )
        
        user_email = str(user_email).strip()
        session_name = str(session_name).strip() if session_name else None
        
        if "@" not in user_email or "." not in user_email:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid user email format: '{user_email}'"
            )
        
        print(f"✅ MANUAL PARSING SUCCESS: user_email = '{user_email}'")
        
        return CandidateEvaluationResponse(
            status="success",
            message=f"Manual parsing successful for user: {user_email}",
            results=[],
            summary={"total_processed": 0, "accepted": 0, "rejected": 0, "errors": 0}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Manual parsing error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Manual parsing error: {str(e)}")

@router.get("/users/{user_email}/sessions")
async def get_user_sessions(user_email: str):
    """Get all evaluation sessions for a user"""
    user = await db_service.create_or_get_user(user_email)
    sessions = await db_service.get_user_sessions(user["id"])
    return {"sessions": sessions}

@router.get("/sessions/{session_id}/candidates")
async def get_session_candidates(session_id: str):
    """Get all candidates for a specific session"""
    candidates = await db_service.get_session_candidates(session_id)
    return {"candidates": candidates}

@router.get("/candidates/{candidate_id}")
async def get_candidate_detail(candidate_id: str):
    """Get detailed information about a specific candidate"""
    candidate = await db_service.get_candidate_detail(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.get("/users/{user_email}/criteria")
async def get_user_criteria(user_email: str):
    """Get user-specific eligibility criteria"""
    user = await db_service.create_or_get_user(user_email)
    criteria = await db_service.get_user_criteria(user["id"])
    if criteria:
        return {"status": "success", "content": criteria}
    else:
        # Fall back to default criteria
        return await get_eligibility_criteria()

@router.put("/users/{user_email}/criteria")
async def update_user_criteria(user_email: str, request: EligibilityCriteriaUpdate):
    """Update user-specific eligibility criteria"""
    user = await db_service.create_or_get_user(user_email)
    criteria_id = await db_service.save_user_criteria(user["id"], request.content)
    return {
        "status": "success",
        "message": "User criteria updated successfully",
        "criteria_id": criteria_id
    }

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

@router.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy", 
        "message": "App Reviewer Backend is running",
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
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
        
        # Validate that content is not empty
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="Eligibility criteria content cannot be empty")
        
        # Create backup of current file
        backup_path = f"src/prompt_components/templates/eligibility_criteria_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        shutil.copy2(criteria_file_path, backup_path)
        
        # Write new content
        with open(criteria_file_path, 'w', encoding='utf-8') as file:
            file.write(request.content)
        
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

@router.delete("/users/{user_email}/sessions")
async def delete_user_sessions(user_email: str):
    """Delete all evaluation sessions and candidates for a user"""
    try:
        user = await db_service.create_or_get_user(user_email)
        user_id = user["id"]
        
        # Get all sessions for the user
        sessions = await db_service.get_user_sessions(user_id)
        
        deleted_sessions = 0
        deleted_candidates = 0
        
        for session in sessions:
            session_id = session["id"]
            
            # Delete all candidates for this session
            candidates_deleted = await db_service.delete_session_candidates(session_id)
            deleted_candidates += candidates_deleted
            
            # Delete the session
            await db_service.delete_session(session_id)
            deleted_sessions += 1
        
        return {
            "status": "success",
            "message": f"Deleted {deleted_sessions} sessions and {deleted_candidates} candidate evaluations",
            "deleted_sessions": deleted_sessions,
            "deleted_candidates": deleted_candidates
        }
    except Exception as e:
        print(f"Error deleting user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting sessions: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session and all its candidates"""
    try:
        # Delete all candidates for this session
        candidates_deleted = await db_service.delete_session_candidates(session_id)
        
        # Delete the session
        session_deleted = await db_service.delete_session(session_id)
        
        if session_deleted:
            return {
                "status": "success",
                "message": f"Deleted session and {candidates_deleted} candidate evaluations",
                "deleted_candidates": candidates_deleted
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")