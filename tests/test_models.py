"""
Tests for Pydantic models.
"""
import pytest
from models import (
    ArticleRequest, SERPResult, KeywordAnalysis,
    InternalLink, ExternalReference, FAQItem,
    JobStatus
)


def test_article_request_valid():
    """Test valid article request."""
    request = ArticleRequest(
        topic="test topic",
        target_word_count=1500,
        language="en"
    )
    assert request.topic == "test topic"
    assert request.target_word_count == 1500
    assert request.language == "en"


def test_article_request_defaults():
    """Test article request with defaults."""
    request = ArticleRequest(topic="test")
    assert request.target_word_count == 1500
    assert request.language == "en"


def test_article_request_validation():
    """Test article request validation."""
    with pytest.raises(ValueError):
        ArticleRequest(topic="", target_word_count=1500)
    
    with pytest.raises(ValueError):
        ArticleRequest(topic="test", target_word_count=100)  # Too low
    
    with pytest.raises(ValueError):
        ArticleRequest(topic="test", target_word_count=10000)  # Too high


def test_serp_result():
    """Test SERP result model."""
    result = SERPResult(
        rank=1,
        url="https://example.com",
        title="Test Title",
        snippet="Test snippet"
    )
    assert result.rank == 1
    assert result.url == "https://example.com"


def test_keyword_analysis():
    """Test keyword analysis model."""
    analysis = KeywordAnalysis(
        primary_keyword="test",
        secondary_keywords=["keyword1", "keyword2"],
        keyword_density={"test": 1.5, "keyword1": 0.8}
    )
    assert analysis.primary_keyword == "test"
    assert len(analysis.secondary_keywords) == 2


def test_internal_link():
    """Test internal link model."""
    link = InternalLink(
        anchor_text="test link",
        target_page="/test",
        context="In the introduction"
    )
    assert link.anchor_text == "test link"
    assert link.target_page == "/test"


def test_external_reference():
    """Test external reference model."""
    ref = ExternalReference(
        url="https://example.com",
        title="Test Reference",
        context="In the body",
        citation_text="According to example.com"
    )
    assert ref.url == "https://example.com"
    assert ref.title == "Test Reference"


def test_faq_item():
    """Test FAQ item model."""
    faq = FAQItem(
        question="What is test?",
        answer="Test is a thing."
    )
    assert faq.question == "What is test?"
    assert faq.answer == "Test is a thing."

