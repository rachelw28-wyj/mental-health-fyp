from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users" # Changed to lowercase plural

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('Patient', 'Professional'), default='Patient', nullable=False)
    created_at = Column(DateTime, default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history" # Lowercase

    msg_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE")) # Updated FK
    sender = Column(Enum('User', 'Bot'), nullable=False)
    message_text = Column(Text, nullable=False)
    sentiment_score = Column(Float)
    timestamp = Column(DateTime, default=func.now())

class MoodLog(Base):
    __tablename__ = "mood_logs" # Lowercase

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE")) # Updated FK
    mood_rating = Column(Integer, nullable=False)
    primary_emotion = Column(String(50), nullable=False)
    note = Column(Text)
    log_date = Column(Date, nullable=False)

class JournalEntry(Base):
    __tablename__ = "journal_entries" # Lowercase

    journal_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE")) # Updated FK
    title = Column(String(100))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

class CrisisEvent(Base):
    __tablename__ = "crisis_events" # Lowercase

    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE")) # Updated FK
    trigger_word = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False)
    action_taken = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=func.now())