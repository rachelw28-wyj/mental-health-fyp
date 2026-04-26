from pydantic import BaseModel, Field
from datetime import datetime, date

# 1. What the API expects to RECEIVE from the user
class ChatMessageCreate(BaseModel):
    user_id: int
    message_text: str

# 2. What the API will SEND BACK to the user
class ChatMessageResponse(BaseModel):
    msg_id: int
    sender: str
    message_text: str
    timestamp: datetime

    # This tells Pydantic to safely read the data coming from SQLAlchemy models
    class Config:
        from_attributes = True


# --- MOOD TRACKING SCHEMAS ---

# What the API expects to RECEIVE from the user
class MoodLogCreate(BaseModel):
    user_id: int
    mood_rating: int  # Expecting a number from 1 to 5
    primary_emotion: str
    note: str = None  # Optional text note
    log_date: date

# What the API will SEND BACK to confirm it saved
class MoodLogResponse(BaseModel):
    log_id: int
    user_id: int
    mood_rating: int
    primary_emotion: str
    note: str | None = None
    log_date: date

    class Config:
        from_attributes = True


# --- JOURNALING SCHEMAS ---

# What the API expects to RECEIVE when a user writes a journal entry
class JournalEntryCreate(BaseModel):
    user_id: int
    title: str | None = None  # Title is optional
    content: str

# What the API will SEND BACK to the frontend
class JournalEntryResponse(BaseModel):
    journal_id: int
    user_id: int
    title: str | None = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- USER ACCOUNT SCHEMAS ---

# What the API expects to RECEIVE when a new user signs up
class UserCreate(BaseModel):
    username: str
    email: str
    password: str = Field(..., max_length=64)
    role: str = "Patient" # Defaults to Patient, but allows "Professional" during signup

# What the API expects to RECEIVE when a user tries to log in
class UserLogin(BaseModel):
    email: str
    password: str

# What the API will SEND BACK
class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True