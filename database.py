"""
Database models and setup for job persistence.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()


class Job(Base):
    """Database model for article generation jobs."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    target_word_count = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "status": self.status,
            "topic": self.topic,
            "target_word_count": self.target_word_count,
            "language": self.language,
            "result": self.result,
            "error_message": self.error_message,
            "progress": self.progress,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


# SQLite database setup
DATABASE_URL = "sqlite:///./article_generation.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

