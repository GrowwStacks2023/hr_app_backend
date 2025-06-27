# controllers/job_controller.py
from ast import List
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from routers.Jobs.jobs_model import Job, JobCreate, JobRead
import shutil
import os
from routers.Candidate.candidate_model import Candidate, CandidateRead
import openai
import pdfplumber


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Set API Key directly (Not recommended — see note below)
openai.api_key = "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"

@router.post("/apply/{company_id}")
async def apply_job(
    company_id: str,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    qualification: str = Form(...),
    designation: str = Form(...),
    department: str = Form(...),
    job_id: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # ✅ Save resume file
        upload_dir = "resumes"
        os.makedirs(upload_dir, exist_ok=True)
        if not resume.filename:
            raise HTTPException(status_code=400, detail="No resume file uploaded")
        file_path = os.path.join(upload_dir, os.path.basename(resume.filename))

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        # ✅ Get job details
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job or not getattr(job, "description", None):
            raise HTTPException(status_code=404, detail="Job not found or missing description")

        job_description = job.description
        resumeScreenQualificationScore = job.resumeScreenQualificationScore

        # ✅ Extract resume text using pdfplumber
        def extract_text_from_pdf(path):
            with pdfplumber.open(path) as pdf:
                return "\n".join([page.extract_text() or "" for page in pdf.pages])

        resume_text = extract_text_from_pdf(file_path)

        # ✅ Build AI prompt
        prompt = f"""
You are an expert HR AI assistant specialized in matching candidate resumes with job descriptions.

Your task is to analyze the compatibility between a job posting and a candidate's resume, then provide a comprehensive scoring and decision.

## Job Description:
{job_description}

## Resume:
{resume_text}

## Instructions:
1. Score the candidate on Technical Skills, Experience, Soft Skills, and Bonus Qualifications.
2. Use scoring rules:
  - 90–100: Exceptional match
  - 80–89: Strong match
  - 70–79: Good match
  - 60–69: Fair match
  - Below 60: Poor match
3. Result:
  - If score >= {resumeScreenQualificationScore} → "SELECT CANDIDATE"
  - Else → "REJECT CANDIDATE"

## Output Format:
Respond ONLY in valid JSON. No markdown, no explanation.

Format:
{{
  "score": 0–100,
  "result": "SELECT CANDIDATE" or "REJECT CANDIDATE",
  "reason": "Brief justification for the decision"
}}

Respond in JSON format only.
"""

        # ✅ OpenAI API call (use correct method)
        response = openai.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},  # JSON-enforced response
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # ✅ Extract response content
        content = response.choices[0].message.content if response.choices[0].message and response.choices[0].message.content else None
        if not content:
            raise HTTPException(status_code=500, detail="AI response did not contain any content.")
        try:
            analysis_json = json.loads(content)
        except Exception:
            raise HTTPException(status_code=500, detail="AI response was not valid JSON.")

        score = analysis_json.get("score")
        result = analysis_json.get("result")
        reason = analysis_json.get("reason")

        print(score)
        print(result)
        print(reason)

        # ✅ Save candidate in DB
        new_candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            qualification=qualification,
            designation=designation,
            department=department,
            resume_path=file_path,
            company_id=company_id,
            job_id=job_id,
            resume_screen_score=score,
            screening_result=result,
            screening_reason_result=reason
        )

        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)

        return {
            "message": "Application submitted",
            "candidate": {
                "id": new_candidate.id,
                "name": new_candidate.name,
                "email": new_candidate.email,
                "score": score,
                "result": result,
                "reason": reason
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# 🟡 Get All Candidates
@router.get("/candidates/{company_id}")
def list_all_candidates(company_id: int, db: Session = Depends(get_db)):
    # Join Candidate with Job and fetch necessary fields
    results = (
        db.query(
            Candidate,
            Job.title.label("job_title")
        )
        .join(Job, Candidate.job_id == Job.id, isouter=True)  # left outer join to include candidates without job
        .filter(Candidate.company_id == company_id)
        .all()
    )

    candidates = []
    for candidate, job_title in results:
        candidates.append({
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "qualification": candidate.qualification,
            "designation": candidate.designation,
            "department": candidate.department,
            "job_id": candidate.job_id,
            "resume_path": candidate.resume_path,
            "job_title": job_title,
            "created_at": candidate.created_at,
            "resume_screen_score": candidate.resume_screen_score,
            "screening_result": candidate.screening_result,
            "screening_reason_result": candidate.screening_reason_result
        })

    return candidates



@router.get("/candidateinfo/{candidate_id}")
def get_candidate_info(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate