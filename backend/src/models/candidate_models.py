from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class CandidateReview(BaseModel):
    outcome: str = Field(..., description="The final outcome of the CandidateReview evaluation either 'Accepted' or 'Rejected'")
    rationale: str = Field(..., description="The rationale for the final outcome")
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )

class ProcessingResult(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    email: str
    name: str
    cv_text: str = ""
    video_transcript: str = ""
    errors: List[str] = []

class ComprehensiveEvaluation(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    outcome: str
    score: float
    rationale: str
    timestamp: str
    email: str
    name: str
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    marital_status: Optional[str] = None
    religion: Optional[str] = None
    phone_number: Optional[str] = None
    residential_address: Optional[str] = None
    current_employment: Optional[str] = None
    employment_category: Optional[str] = None
    company_address: Optional[str] = None
    university_attended: Optional[str] = None
    undergraduate_degree_type: Optional[str] = None
    undergraduate_programme: Optional[str] = None
    undergraduate_class: Optional[str] = None
    undergraduate_completion_date: Optional[str] = None
    postgraduate_degree_type: Optional[str] = None
    postgraduate_programme: Optional[str] = None
    postgraduate_class: Optional[str] = None
    postgraduate_completion_date: Optional[str] = None
    education_qualifications: Optional[str] = None
    professional_qualifications: Optional[str] = None
    career_interests: Optional[str] = None
    msa_interests: Optional[str] = None  # Fixed: use msa_interests to match DB
    previous_applications: Optional[str] = None
    candidate_essay: str
    cv_url: str
    video_url: str
    cv_text: str
    video_transcript: str
    processing_errors: List[str]
    evaluation_timestamp: str
    files_processed_successfully: bool

class CandidateEvaluationRequest(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    candidates_csv: str = Field(..., description="Base64 encoded CSV content or file path")
    
class CandidateEvaluationResponse(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    status: str
    message: str
    results: List[dict]
    summary: dict
    session_id: Optional[str] = None