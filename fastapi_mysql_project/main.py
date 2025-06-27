# main.py
from database import engine, Base  # <-- ADD THIS
from routers.User.user_controller import router as user_controller  
from routers.Jobs.jobs_controller import router as jobs_controller
from routers.Candidate.candidate_controller import router as candidate_controller
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

app = FastAPI()

# ✅ Add this line to auto-create missing columns
Base.metadata.create_all(bind=engine)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or set your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(user_controller)
app.include_router(jobs_controller)
app.include_router(candidate_controller)