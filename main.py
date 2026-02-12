"""
FastAPI application for SEO article generation.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any

from models import ArticleRequest, ArticleResponse, JobStatusResponse, JobStatus
from database import init_db, get_db
from serp_service import SERPService
from article_generator import ArticleGenerator
from job_service import JobService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="SEO Article Generation API",
    description="AI-powered SEO article generation service",
    version="1.0.0",
    lifespan=lifespan
)


async def generate_article_task(
    job_id: str,
    topic: str,
    target_word_count: int,
    language: str
):
    """
    Background task for article generation.
    
    Args:
        job_id: Job identifier
        topic: Article topic
        target_word_count: Target word count
        language: Language code
    """
    # Create a new database session for the background task
    from database import SessionLocal
    db = SessionLocal()
    try:
        job_service = JobService(db)
        serp_service = SERPService(use_mock=True)  # Use mock for now
        article_generator = ArticleGenerator()
        
        # Update status to running
        job_service.update_job_status(
            job_id,
            JobStatus.RUNNING,
            progress={"stage": "fetching_serp"}
        )
        
        # Step 1: Fetch SERP results
        serp_results = await serp_service.fetch_results(topic, language)
        
        job_service.update_job_status(
            job_id,
            JobStatus.RUNNING,
            progress={"stage": "analyzing_themes", "serp_count": len(serp_results)}
        )
        
        # Step 2: Analyze themes
        themes = serp_service.analyze_themes(serp_results)
        
        job_service.update_job_status(
            job_id,
            JobStatus.RUNNING,
            progress={"stage": "generating_article", "themes_count": len(themes)}
        )
        
        # Step 3: Generate article
        article_data = await article_generator.generate_article(
            topic, serp_results, themes, target_word_count, language
        )
        
        # Step 4: Create article content object
        from models import ArticleContent
        article_content = ArticleContent(**article_data)
        
        # Step 5: Combine all content
        full_content = (
            article_content.introduction + "\n\n" +
            "\n\n".join([h.get("content", "") for h in article_content.headings]) +
            "\n\n" + article_content.body +
            "\n\n" + article_content.conclusion
        )
        
        # Step 6: Analyze keywords
        keyword_analysis = article_generator.analyze_keywords(full_content, topic)
        
        # Step 7: Generate internal links
        internal_links = article_generator.generate_internal_links(topic)
        
        # Step 8: Generate external references
        external_references = article_generator.generate_external_references(topic)
        
        # Step 9: Generate FAQ
        faq_section = article_generator.generate_faq(serp_results, topic)
        
        # Step 10: Validate SEO
        seo_validation = article_generator.validate_seo(article_content, keyword_analysis)
        
        # Calculate word count
        word_count = len(full_content.split())
        
        job_service.update_job_status(
            job_id,
            JobStatus.RUNNING,
            progress={"stage": "finalizing", "word_count": word_count, "seo_score": seo_validation["score"]}
        )
        
        # Prepare result
        result: Dict[str, Any] = {
            "word_count": word_count,
            "content": article_content.model_dump(),
            "keyword_analysis": keyword_analysis.model_dump(),
            "internal_links": [link.model_dump() for link in internal_links],
            "external_references": [ref.model_dump() for ref in external_references],
            "faq_section": [faq.model_dump() for faq in faq_section],
            "serp_analysis": [result.model_dump() for result in serp_results],
            "seo_validation": seo_validation
        }
        
        # Update job as completed
        job_service.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            result=result
        )
        
    except Exception as e:
        # Update job as failed
        error_message = str(e)
        if 'job_service' in locals():
            job_service.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=error_message
            )
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SEO Article Generation API",
        "version": "1.0.0",
        "endpoints": {
            "POST /generate": "Generate a new article",
            "GET /jobs/{job_id}": "Get job status",
            "GET /jobs/{job_id}/result": "Get article result"
        }
    }


@app.post("/generate", response_model=Dict[str, str])
async def generate_article(
    request: ArticleRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate an SEO-optimized article.
    
    This endpoint creates a job and returns immediately with a job ID.
    The article generation happens in the background.
    """
    job_service = JobService(db)
    
    # Create job
    job_id = job_service.create_job(
        topic=request.topic,
        target_word_count=request.target_word_count,
        language=request.language
    )
    
    # Start background task
    background_tasks.add_task(
        generate_article_task,
        job_id,
        request.topic,
        request.target_word_count,
        request.language
    )
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Article generation started. Use the job_id to check status."
    }


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status of an article generation job.
    """
    job_service = JobService(db)
    status = job_service.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status


@app.get("/jobs/{job_id}/result", response_model=ArticleResponse)
async def get_job_result(job_id: str, db: Session = Depends(get_db)):
    """
    Get the complete article result for a completed job.
    """
    job_service = JobService(db)
    result = job_service.get_job_response(job_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if result.status == JobStatus.PENDING or result.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"Job is still {result.status.value}. Please wait for completion."
        )
    
    return result


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

