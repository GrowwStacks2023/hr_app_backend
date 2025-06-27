# models/user_model.py
from sqlalchemy import Column, Integer, String
from database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))  # Store hashed passwords in real apps

# For request/response models
from pydantic import BaseModel

class UserLogin(BaseModel):
    email: str
    password: str



class UserResponse(BaseModel):
    id: int
    name: str
    email: str
