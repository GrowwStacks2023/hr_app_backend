# models/candidate_model.py
import datetime
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text
from database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(100), nullable=False)
    job_id = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    qualification = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    resume_path = Column(Text, nullable=True)  # Store file path or filename
    created_at = Column(DateTime, default=datetime.datetime.now)
    resume_screen_score = Column(String(100), nullable=True)
    screening_result = Column(Text, nullable=True)
    screening_reason_result = Column(Text, nullable=True)

class CandidateCreate(BaseModel):
    company_id: str
    job_id: str
    name: str
    email: str
    phone: str
    qualification: str
    designation: str
    department: str
    resume_screen_score: str
    screening_result: str
    screening_reason_result: str
    

class CandidateRead(CandidateCreate):
    id: int

    class Config:
        orm_mode = True


