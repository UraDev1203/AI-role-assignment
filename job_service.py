"""
Job management service for article generation.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models import JobStatus, ArticleResponse, JobStatusResponse
from database import Job, get_db


class JobService:
    """Service for managing article generation jobs."""
    
    def __init__(self, db: Session):
        """Initialize job service with database session."""
        self.db = db
    
    def create_job(
        self,
        topic: str,
        target_word_count: int,
        language: str
    ) -> str:
        """
        Create a new article generation job.
        
        Args:
            topic: Article topic/keyword
            target_word_count: Target word count
            language: Language code
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            status=JobStatus.PENDING.value,
            topic=topic,
            target_word_count=target_word_count,
            language=language,
            progress={"stage": "initialized"}
        )
        self.db.add(job)
        self.db.commit()
        return job_id
    
    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        progress: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update job status and related data.
        
        Args:
            job_id: Job identifier
            status: New status
            result: Job result data
            error_message: Error message if failed
            progress: Progress information
            
        Returns:
            True if job was updated, False if not found
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        
        job.status = status.value
        if result is not None:
            job.result = result
        if error_message:
            job.error_message = error_message
        if progress:
            job.progress = progress
        if status == JobStatus.COMPLETED or status == JobStatus.FAILED:
            job.completed_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job object or None if not found
        """
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def get_job_status(self, job_id: str) -> Optional[JobStatusResponse]:
        """
        Get job status response.
        
        Args:
            job_id: Job identifier
            
        Returns:
            JobStatusResponse or None if not found
        """
        job = self.get_job(job_id)
        if not job:
            return None
        
        return JobStatusResponse(
            job_id=job.id,
            status=JobStatus(job.status),
            created_at=job.created_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            progress=job.progress
        )
    
    def get_job_response(self, job_id: str) -> Optional[ArticleResponse]:
        """
        Get complete article response for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            ArticleResponse or None if not found
        """
        job = self.get_job(job_id)
        if not job:
            return None
        
        # Convert job to ArticleResponse
        result = job.result or {}
        
        return ArticleResponse(
            job_id=job.id,
            status=JobStatus(job.status),
            topic=job.topic,
            word_count=result.get("word_count", 0),
            content=result.get("content"),
            keyword_analysis=result.get("keyword_analysis"),
            internal_links=result.get("internal_links", []),
            external_references=result.get("external_references", []),
            faq_section=result.get("faq_section", []),
            serp_analysis=result.get("serp_analysis"),
            created_at=job.created_at,
            completed_at=job.completed_at,
            error_message=job.error_message
        )

