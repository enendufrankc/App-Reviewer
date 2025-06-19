import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

from src.config.settings import AppConfig

class DatabaseService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = None
        
        if config.supabase_url and config.database_key:
            try:
                # Use the working connection pattern from your test
                options = ClientOptions(function_client_timeout=15)
                self.client = create_client(
                    config.supabase_url, 
                    config.database_key,  # Use the correct key
                    options=options
                )
                print("Supabase client initialized successfully")
            except Exception as e:
                print(f"Error initializing Supabase client: {str(e)}")
                self.client = None
        else:
            print("Supabase client not initialized - missing URL or API key")
            if not config.supabase_url:
                print("  Missing: SUPABASE_URL")
            if not config.database_key:
                print("  Missing: Valid Supabase API key (SUPABASE_SERVICE_ROLE_KEY, SUPABASE_KEY, or SUPABASE_ANON_KEY)")
    
    def is_available(self) -> bool:
        """Check if database is available"""
        return self.client is not None
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        if not self.is_available():
            return False
        
        try:
            # Test with a simple query that should work with any key
            result = self.client.table("candidate_evaluations").select("count", count="exact").limit(1).execute()
            print(f"Connection test successful - found table with {result.count} records")
            return True
        except Exception as e:
            print(f"Database connection test failed: {str(e)}")
            # Try alternative test
            try:
                # Test with a different approach
                result = self.client.table("candidate_evaluations").select("*").limit(0).execute()
                print("Connection test successful with alternative method")
                return True
            except Exception as e2:
                print(f"Alternative connection test also failed: {str(e2)}")
                return False
    
    async def create_tables(self):
        """Create all database tables - handled by Supabase migrations"""
        if not self.is_available():
            raise Exception("Database service not available - check your Supabase configuration")
        
        try:
            # Test connection first
            if not await self.test_connection():
                raise Exception("Cannot connect to database - check your network connection and credentials")
            
            print("Database tables managed by Supabase - no manual creation needed")
        except Exception as e:
            print(f"Error accessing database: {str(e)}")
            raise
    
    # User Management
    async def create_or_get_user(self, email: str, name: str = None) -> Dict[str, Any]:
        """Create a new user or get existing user by email"""
        try:
            # Check if user exists
            result = self.client.table("users").select("*").eq("email", email).execute()
            
            if result.data:
                user = result.data[0]
                # Update name if provided and different - use updated_at since column exists
                if name and user.get("name") != name:
                    update_result = self.client.table("users").update({
                        "name": name,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }).eq("id", user["id"]).execute()
                    user = update_result.data[0]
            else:
                # Create new user - timestamps are auto-generated but we can set them
                user_data = {
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "name": name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                create_result = self.client.table("users").insert(user_data).execute()
                user = create_result.data[0]
            
            return {
                "id": user["id"],
                "email": user["email"],
                "name": user.get("name"),
                "created_at": user.get("created_at", datetime.now(timezone.utc).isoformat())
            }
        except Exception as e:
            print(f"Error creating/getting user: {str(e)}")
            # Return a default user for now
            return {
                "id": str(uuid.uuid4()),
                "email": email,
                "name": name,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
    
    # Evaluation Session Management
    async def create_evaluation_session(self, user_id: str, session_name: str = None) -> str:
        """Create a new evaluation session"""
        try:
            session_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": session_name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "status": "processing"
            }
            
            result = self.client.table("evaluation_sessions").insert(session_data).execute()
            return result.data[0]["id"]
        except Exception as e:
            print(f"Error creating evaluation session: {str(e)}")
            return str(uuid.uuid4())  # Fallback
    
    async def update_session_progress(
        self,
        session_id: str,
        processed_candidates: int = None,
        accepted_count: int = None,
        rejected_count: int = None,
        error_count: int = None,
        current_batch: int = None,
        total_candidates: int = None,
        status: str = None
    ):
        """Update session progress"""
        try:
            update_data = {}
            
            if processed_candidates is not None:
                update_data["processed_candidates"] = processed_candidates
            if accepted_count is not None:
                update_data["accepted_count"] = accepted_count
            if rejected_count is not None:
                update_data["rejected_count"] = rejected_count
            if error_count is not None:
                update_data["error_count"] = error_count
            if current_batch is not None:
                update_data["current_batch"] = current_batch
            if total_candidates is not None:
                update_data["total_candidates"] = total_candidates
            if status is not None:
                update_data["status"] = status
            
            # Calculate progress percentage
            if total_candidates and processed_candidates:
                update_data["progress_percentage"] = (processed_candidates / total_candidates) * 100
            
            if update_data:  # Only update if there's data to update
                self.client.table("evaluation_sessions").update(update_data).eq("id", session_id).execute()
        except Exception as e:
            print(f"Error updating session progress: {str(e)}")
    
    async def complete_session(self, session_id: str, summary: Dict[str, Any]):
        """Mark session as completed"""
        try:
            update_data = {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),  # Column exists
                "total_candidates": summary.get("total_processed", 0),
                "processed_candidates": summary.get("total_processed", 0),
                "accepted_count": summary.get("accepted", 0),
                "rejected_count": summary.get("rejected", 0),
                "error_count": summary.get("errors", 0),
                "progress_percentage": 100.0
            }
            
            self.client.table("evaluation_sessions").update(update_data).eq("id", session_id).execute()
        except Exception as e:
            print(f"Error completing session: {str(e)}")
    
    # Candidate Evaluation Management
    async def save_candidate_evaluation(self, session_id: str, candidate_data: Dict[str, Any]) -> str:
        """Save candidate evaluation to database - overwrite if candidate email already exists"""
        try:
            candidate_email = candidate_data.get("email", "")
            
            # Check if candidate already exists in this session or any other session
            existing_result = self.client.table("candidate_evaluations").select("id, session_id").eq("email", candidate_email).execute()
            
            # Remove timestamp fields since they're likely auto-generated by Supabase
            candidate_data.pop("created_at", None)
            candidate_data.pop("evaluation_timestamp", None)
            candidate_data.pop("updated_at", None)
            
            # Clean the data - remove any None values and convert lists to JSON strings
            cleaned_data = {}
            for key, value in candidate_data.items():
                if value is None:
                    cleaned_data[key] = ""
                elif isinstance(value, list):
                    cleaned_data[key] = json.dumps(value) if value else ""
                else:
                    cleaned_data[key] = value
            
            if existing_result.data:
                # Candidate exists - update the existing record
                existing_candidate = existing_result.data[0]
                existing_id = existing_candidate["id"]
                
                print(f"💾 Updating existing candidate: {candidate_email} (ID: {existing_id})")
                
                # Update with new session_id and evaluation data
                cleaned_data["session_id"] = session_id
                
                result = self.client.table("candidate_evaluations").update(cleaned_data).eq("id", existing_id).execute()
                
                if result.data:
                    print(f"✅ Successfully updated candidate: {candidate_email}")
                    return result.data[0]["id"]
                else:
                    print(f"⚠️  No data returned from update operation")
                    return existing_id
            else:
                # New candidate - insert as before
                candidate_id = str(uuid.uuid4())
                cleaned_data["id"] = candidate_id
                cleaned_data["session_id"] = session_id
                
                print(f"💾 Saving new candidate: {candidate_email} to session {session_id}")
                print(f"🔧 Final data keys: {list(cleaned_data.keys())}")
                
                result = self.client.table("candidate_evaluations").insert(cleaned_data).execute()
                
                if result.data:
                    print(f"✅ Successfully saved new candidate with ID: {candidate_id}")
                    return result.data[0]["id"]
                else:
                    print(f"⚠️  No data returned from insert operation")
                    return candidate_id
                    
        except Exception as e:
            print(f"❌ Error saving candidate evaluation: {str(e)}")
            print(f"   Candidate data keys: {list(candidate_data.keys()) if candidate_data else 'None'}")
            print(f"   Session ID: {session_id}")
            return str(uuid.uuid4())  # Fallback
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        try:
            result = self.client.table("evaluation_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data
        except Exception as e:
            print(f"Error getting user sessions: {str(e)}")
            return []
    
    async def get_session_candidates(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for a specific session"""
        try:
            # Use the correct column name: evaluation_timestamp exists
            result = self.client.table("candidate_evaluations").select("id, outcome, score, rationale, email, name, evaluation_timestamp").eq("session_id", session_id).order("evaluation_timestamp", desc=True).execute()
            return result.data
        except Exception as e:
            print(f"Error getting session candidates: {str(e)}")
            return []
    
    async def get_candidate_detail(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific candidate"""
        try:
            result = self.client.table("candidate_evaluations").select("*").eq("id", candidate_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting candidate detail: {str(e)}")
            return None
    
    # User Criteria Management
    async def save_user_criteria(self, user_id: str, content: str) -> str:
        """Save user-specific criteria"""
        try:
            # Deactivate existing criteria
            self.client.table("user_criteria").update({"is_active": False}).eq("user_id", user_id).execute()
            
            # Create new active criteria
            criteria_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "content": content,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = self.client.table("user_criteria").insert(criteria_data).execute()
            return result.data[0]["id"]
        except Exception as e:
            print(f"Error saving user criteria: {str(e)}")
            return str(uuid.uuid4())  # Fallback
    
    async def get_user_criteria(self, user_id: str) -> Optional[str]:
        """Get active user criteria"""
        try:
            result = self.client.table("user_criteria").select("content").eq("user_id", user_id).eq("is_active", True).order("created_at", desc=True).limit(1).execute()
            return result.data[0]["content"] if result.data else None
        except Exception as e:
            print(f"Error getting user criteria: {str(e)}")
            return None
    
    async def get_active_criteria(self, user_id: str):
        """Get active criteria object for a user"""
        try:
            result = self.client.table("user_criteria").select("*").eq("user_id", user_id).eq("is_active", True).order("created_at", desc=True).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting active criteria: {str(e)}")
            return None
    
    async def delete_session_candidates(self, session_id: str) -> int:
        """Delete all candidates for a specific session"""
        try:
            # Get count first
            result = self.client.table("candidate_evaluations").select("id").eq("session_id", session_id).execute()
            count = len(result.data)
            
            # Delete candidates
            self.client.table("candidate_evaluations").delete().eq("session_id", session_id).execute()
            
            print(f"✅ Deleted {count} candidates from session {session_id}")
            return count
        except Exception as e:
            print(f"Error deleting session candidates: {str(e)}")
            return 0
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        try:
            result = self.client.table("evaluation_sessions").delete().eq("id", session_id).execute()
            print(f"✅ Deleted session {session_id}")
            return True
        except Exception as e:
            print(f"Error deleting session: {str(e)}")
            return False