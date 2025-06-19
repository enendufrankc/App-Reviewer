from .candidate_models import CandidateReview, ProcessingResult, ComprehensiveEvaluation, CandidateEvaluationRequest, CandidateEvaluationResponse
from .evaluation_models import EligibilityCriteriaUpdate, EligibilityCriteriaValidation
try:
    from .database_models import User, EvaluationSession, CandidateEvaluation, UserCriteria, UserCredentials
    DATABASE_MODELS_AVAILABLE = True
except ImportError:
    DATABASE_MODELS_AVAILABLE = False
    print("Warning: Database models not available - check SQLAlchemy installation")

__all__ = [
    "CandidateReview", "ProcessingResult", "ComprehensiveEvaluation", 
    "CandidateEvaluationRequest", "CandidateEvaluationResponse",
    "EligibilityCriteriaUpdate", "EligibilityCriteriaValidation"
]

if DATABASE_MODELS_AVAILABLE:
    __all__.extend(["User", "EvaluationSession", "CandidateEvaluation", "UserCriteria", "UserCredentials"])