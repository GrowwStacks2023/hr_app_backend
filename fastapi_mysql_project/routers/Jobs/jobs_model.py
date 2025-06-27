# models/job_model.py
from sqlalchemy import Column, Integer, String, Text
from database import Base
from pydantic import BaseModel
from typing import Optional


# --- SQLAlchemy Model ---
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    resumeScreenInstructions = Column(Text, nullable=True)
    resumeScreenQualificationScore = Column(String(50), nullable=True)
    technicalAssessmentInstructions = Column(Text, nullable=True)
    technicalAssessmentScore = Column(String(50), nullable=True)
    teleinterviewinstruction = Column(Text, nullable=True)
    teleinterviewscore = Column(String(50), nullable=True)
    teleRoundPrompt = Column(Text, nullable=True)
    teleRoundScore = Column(String(50), nullable=True)
    companyName = Column(String(255), nullable=True)
    status = Column(String(50), default='draft', nullable=True)
    createdBy = Column(Integer, nullable=True)  # change to Integer if using user_id


# --- Pydantic Schemas ---
class JobCreate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    resumeScreenInstructions: Optional[str] = None
    resumeScreenQualificationScore: Optional[str] = None
    technicalAssessmentInstructions: Optional[str] = None
    technicalAssessmentScore: Optional[str] = None
    teleinterviewinstruction: Optional[str] = None
    teleinterviewscore: Optional[str] = None
    teleRoundPrompt: Optional[str] = None
    teleRoundScore: Optional[str] = None
    status: Optional[str] = "draft"
    companyName: Optional[str] = None
    createdBy: Optional[int] = None

class JobRead(JobCreate):
    id: int

    class Config:
        orm_mode = True
