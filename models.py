from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('Patient', 'Professional'), default='Patient', nullable=False)
    created_at = Column(DateTime, default=func.now())

class ChatHistory(Base):
    __tablename__ = "Chat_History"

    msg_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    sender = Column(Enum('User', 'Bot'), nullable=False)
    message_text = Column(Text, nullable=False)
    sentiment_score = Column(Float)
    timestamp = Column(DateTime, default=func.now())

class MoodLog(Base):
    __tablename__ = "Mood_Logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    mood_rating = Column(Integer, nullable=False)
    primary_emotion = Column(String(50), nullable=False)
    note = Column(Text)
    log_date = Column(Date, nullable=False)

class JournalEntry(Base):
    __tablename__ = "Journal_Entries"

    journal_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    title = Column(String(100))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

class CrisisEvent(Base):
    __tablename__ = "Crisis_Events"

    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    trigger_word = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False)
    action_taken = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=func.now())