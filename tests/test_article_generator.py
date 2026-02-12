"""
Tests for article generator.
"""
import pytest
from article_generator import ArticleGenerator
from models import SERPResult


@pytest.fixture
def generator():
    """Create article generator instance."""
    return ArticleGenerator()


@pytest.fixture
def mock_serp_results():
    """Create mock SERP results."""
    return [
        SERPResult(
            rank=i,
            url=f"https://example.com/result{i}",
            title=f"Result {i} Title",
            snippet=f"Result {i} snippet content"
        )
        for i in range(1, 11)
    ]


@pytest.mark.asyncio
async def test_generate_template_article(generator, mock_serp_results):
    """Test template article generation."""
    themes = ["productivity", "tools", "remote", "teams"]
    result = generator._generate_template_article(
        topic="productivity tools",
        serp_results=mock_serp_results,
        themes=themes,
        target_word_count=1500
    )
    
    assert "title" in result
    assert "meta_title" in result
    assert "meta_description" in result
    assert "introduction" in result
    assert "headings" in result
    assert "body" in result
    assert "conclusion" in result
    assert len(result["title"]) > 0
    assert len(result["meta_description"]) > 0


def test_analyze_keywords(generator):
    """Test keyword analysis."""
    content = "This is a test article about productivity tools. Productivity tools are essential for remote teams. Remote teams need productivity tools."
    analysis = generator.analyze_keywords(content, "productivity tools")
    
    assert analysis.primary_keyword == "productivity tools"
    assert len(analysis.secondary_keywords) > 0
    assert "productivity tools" in analysis.keyword_density


def test_generate_internal_links(generator):
    """Test internal link generation."""
    links = generator.generate_internal_links("productivity tools")
    
    assert len(links) == 5
    assert all(link.anchor_text for link in links)
    assert all(link.target_page for link in links)
    assert all(link.context for link in links)


def test_generate_external_references(generator):
    """Test external reference generation."""
    refs = generator.generate_external_references("productivity tools")
    
    assert len(refs) == 4
    assert all(ref.url for ref in refs)
    assert all(ref.title for ref in refs)
    assert all(ref.context for ref in refs)
    assert all(ref.citation_text for ref in refs)


def test_generate_faq(generator, mock_serp_results):
    """Test FAQ generation."""
    faqs = generator.generate_faq(mock_serp_results, "productivity tools")
    
    assert len(faqs) == 4
    assert all(faq.question for faq in faqs)
    assert all(faq.answer for faq in faqs)


def test_validate_seo(generator):
    """Test SEO validation."""
    from models import ArticleContent, KeywordAnalysis
    
    content = ArticleContent(
        title="Productivity Tools Guide",
        meta_title="Productivity Tools Guide 2025",
        meta_description="Discover the best productivity tools for remote teams. Our comprehensive guide covers everything you need to know.",
        introduction="Productivity tools are essential for modern remote teams.",
        headings=[],
        body="Content about productivity tools.",
        conclusion="In conclusion, productivity tools are important."
    )
    
    keyword_analysis = KeywordAnalysis(
        primary_keyword="productivity tools",
        secondary_keywords=["tools", "productivity"],
        keyword_density={"productivity tools": 1.2}
    )
    
    validation = generator.validate_seo(content, keyword_analysis)
    
    assert "is_valid" in validation
    assert "issues" in validation
    assert "warnings" in validation
    assert "score" in validation
    assert isinstance(validation["score"], (int, float))

