"""
Data models for the SEO article generation system.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SERPResult(BaseModel):
    """Single search engine result page entry."""
    rank: int = Field(..., ge=1, le=10, description="Rank position (1-10)")
    url: str = Field(..., description="URL of the result")
    title: str = Field(..., description="Title of the result")
    snippet: str = Field(..., description="Snippet/description of the result")


class KeywordAnalysis(BaseModel):
    """Keyword analysis results."""
    primary_keyword: str = Field(..., description="Main target keyword")
    secondary_keywords: List[str] = Field(default_factory=list, description="Related keywords")
    keyword_density: Dict[str, float] = Field(default_factory=dict, description="Keyword density percentages")


class InternalLink(BaseModel):
    """Internal linking suggestion."""
    anchor_text: str = Field(..., description="Anchor text for the link")
    target_page: str = Field(..., description="Suggested target page/topic")
    context: str = Field(..., description="Context where this link should be placed")


class ExternalReference(BaseModel):
    """External authoritative source reference."""
    url: str = Field(..., description="URL of the authoritative source")
    title: str = Field(..., description="Title of the source")
    context: str = Field(..., description="Context for where to cite this source")
    citation_text: str = Field(..., description="Suggested citation text")


class ArticleRequest(BaseModel):
    """Request model for article generation."""
    topic: str = Field(..., min_length=1, description="Topic or primary keyword")
    target_word_count: int = Field(default=1500, ge=500, le=5000, description="Target word count")
    language: str = Field(default="en", description="Language preference (ISO code)")

    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate topic is not empty."""
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()


class ArticleContent(BaseModel):
    """Generated article content structure."""
    title: str = Field(..., description="Article title (H1)")
    meta_title: str = Field(..., description="SEO meta title tag")
    meta_description: str = Field(..., max_length=160, description="SEO meta description")
    introduction: str = Field(..., description="Article introduction paragraph")
    headings: List[Dict[str, Any]] = Field(default_factory=list, description="Heading hierarchy (H2, H3)")
    body: str = Field(..., description="Full article body content")
    conclusion: str = Field(..., description="Article conclusion")


class FAQItem(BaseModel):
    """FAQ item generated from search results."""
    question: str = Field(..., description="Frequently asked question")
    answer: str = Field(..., description="Answer to the question")


class ArticleResponse(BaseModel):
    """Complete article generation response."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    topic: str = Field(..., description="Original topic/keyword")
    word_count: int = Field(..., description="Actual word count of generated article")
    content: Optional[ArticleContent] = Field(None, description="Generated article content")
    keyword_analysis: Optional[KeywordAnalysis] = Field(None, description="Keyword analysis results")
    internal_links: List[InternalLink] = Field(default_factory=list, description="Internal linking suggestions")
    external_references: List[ExternalReference] = Field(default_factory=list, description="External references")
    faq_section: List[FAQItem] = Field(default_factory=list, description="FAQ section")
    serp_analysis: Optional[List[SERPResult]] = Field(None, description="SERP analysis results")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if job failed")


class JobStatusResponse(BaseModel):
    """Job status response."""
    job_id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None

