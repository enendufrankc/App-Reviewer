from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class CandidateReview(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    outcome: str = Field(..., description="The final outcome of the CandidateReview evaluation either 'Accepted' or 'Rejected'")
    score: float = Field(..., description="The score given to the candidate based on the evaluation criteria")
    rationale: str = Field(..., description="The rationale for the final outcome")

class EligibilityCriteriaUpdate(BaseModel):
    content: str = Field(..., description="The updated eligibility criteria content", min_length=1)

class EligibilityCriteriaValidation(BaseModel):
    content: str = Field(..., description="The eligibility criteria content to validate")