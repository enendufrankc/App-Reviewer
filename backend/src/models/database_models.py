from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    sessions = relationship("EvaluationSession", back_populates="user")
    criteria = relationship("UserCriteria", back_populates="user")
    credentials = relationship("UserCredentials", back_populates="user")

class EvaluationSession(Base):
    __tablename__ = "evaluation_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    total_candidates = Column(Integer, default=0)
    processed_candidates = Column(Integer, default=0)
    accepted_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    current_batch = Column(Integer, default=0)
    total_batches = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    candidates = relationship("CandidateEvaluation", back_populates="session")

class CandidateEvaluation(Base):
    __tablename__ = "candidate_evaluations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("evaluation_sessions.id"), nullable=False)
    
    # AI Evaluation Results
    outcome = Column(String, nullable=False)  # Accepted, Rejected, Error
    score = Column(Float, default=0.0)
    rationale = Column(Text, nullable=True)
    
    # Candidate Data
    timestamp = Column(String, nullable=True)
    email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    religion = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    residential_address = Column(Text, nullable=True)
    current_employment = Column(String, nullable=True)
    employment_category = Column(String, nullable=True)
    company_address = Column(Text, nullable=True)
    university_attended = Column(String, nullable=True)
    undergraduate_degree_type = Column(String, nullable=True)
    undergraduate_programme = Column(String, nullable=True)
    undergraduate_class = Column(String, nullable=True)
    undergraduate_completion_date = Column(String, nullable=True)
    postgraduate_degree_type = Column(String, nullable=True)
    postgraduate_programme = Column(String, nullable=True)
    postgraduate_class = Column(String, nullable=True)
    postgraduate_completion_date = Column(String, nullable=True)
    education_qualifications = Column(Text, nullable=True)
    professional_qualifications = Column(Text, nullable=True)
    career_interests = Column(Text, nullable=True)
    msa_interests = Column(Text, nullable=True)
    previous_applications = Column(String, nullable=True)
    candidate_essay = Column(Text, nullable=True)
    
    # File URLs and Content
    cv_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    cv_text = Column(Text, nullable=True)
    video_transcript = Column(Text, nullable=True)
    
    # Processing metadata
    processing_errors = Column(JSON, nullable=True)
    evaluation_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    files_processed_successfully = Column(Boolean, default=False)
    
    # Relationships
    session = relationship("EvaluationSession", back_populates="candidates")

class UserCriteria(Base):
    __tablename__ = "user_criteria"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="criteria")

class UserCredentials(Base):
    __tablename__ = "user_credentials"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    encrypted_credentials = Column(Text, nullable=False)
    service_type = Column(String, default="google_drive")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="credentials")
