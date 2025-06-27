# controllers/job_controller.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from routers.Jobs.jobs_model import Job, JobCreate, JobRead

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/jobs")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    try:
        print("Received job data:", job.dict())
        new_job = Job(**job.dict())
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job
    except Exception as e:
        print("❌ Error creating job:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

# 🟡 Get All Jobs
@router.get("/jobs", response_model=List[JobRead])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return jobs


# 🟡 Get All Jobs
@router.get("/jobs/{createdBy}", response_model=List[JobRead])
def listall_jobs(createdBy: int, db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.createdBy == createdBy).all()
    return jobs

# 🔴 Delete Job by ID
@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"detail": "Job deleted successfully"}


# ✅ Update job status to "published"
@router.patch("/jobs/{job_id}/publish", response_model=JobRead)
def publish_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "published"  # type: ignore
    db.commit()
    db.refresh(job)
    return job

# ✅ Update job status to "published"
@router.patch("/jobs/{job_id}/closed", response_model=JobRead)
def closed_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "closed"  # type: ignore
    db.commit()
    db.refresh(job)
    return job
