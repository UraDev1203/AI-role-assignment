"""
Tests for SERP service.
"""
import pytest
from serp_service import SERPService


@pytest.mark.asyncio
async def test_fetch_mock_results():
    """Test fetching mock SERP results."""
    service = SERPService(use_mock=True)
    results = await service.fetch_results("productivity tools", "en")
    
    assert len(results) == 10
    assert all(r.rank >= 1 and r.rank <= 10 for r in results)
    assert all(r.url.startswith("http") for r in results)
    assert all(len(r.title) > 0 for r in results)
    assert all(len(r.snippet) > 0 for r in results)


@pytest.mark.asyncio
async def test_analyze_themes():
    """Test theme analysis from SERP results."""
    service = SERPService(use_mock=True)
    results = await service.fetch_results("productivity tools", "en")
    themes = service.analyze_themes(results)
    
    assert len(themes) > 0
    assert isinstance(themes, list)
    assert all(isinstance(theme, str) for theme in themes)


def test_serp_service_initialization():
    """Test SERP service initialization."""
    service = SERPService(use_mock=True)
    assert service.use_mock is True
    
    service = SERPService(use_mock=False)
    assert service.use_mock is False

