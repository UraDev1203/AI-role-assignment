"""
SERP (Search Engine Results Page) analysis service.
Supports both real API integration and mock data for development.
"""
import os
import httpx
from typing import List, Optional
from models import SERPResult
import json
import random


class SERPService:
    """Service for fetching and analyzing search engine results."""
    
    def __init__(self, use_mock: bool = True):
        """
        Initialize SERP service.
        
        Args:
            use_mock: If True, use mock data instead of real API calls
        """
        self.use_mock = use_mock
        self.api_key = os.getenv("SERP_API_KEY", "")
        self.api_provider = os.getenv("SERP_API_PROVIDER", "serpapi")  # serpapi, dataforseo, valueserp
    
    async def fetch_results(self, query: str, language: str = "en") -> List[SERPResult]:
        """
        Fetch top 10 search results for a given query.
        
        Args:
            query: Search query/keyword
            language: Language code
            
        Returns:
            List of SERPResult objects
        """
        if self.use_mock or not self.api_key:
            return self._generate_mock_results(query, language)
        
        try:
            if self.api_provider == "serpapi":
                return await self._fetch_serpapi(query, language)
            elif self.api_provider == "dataforseo":
                return await self._fetch_dataforseo(query, language)
            else:
                return self._generate_mock_results(query, language)
        except Exception as e:
            print(f"Error fetching SERP data: {e}. Falling back to mock data.")
            return self._generate_mock_results(query, language)
    
    def _generate_mock_results(self, query: str, language: str) -> List[SERPResult]:
        """Generate realistic mock SERP results."""
        # Generate mock results based on the query
        mock_templates = [
            {
                "title": f"Top 10 {query.title()} in 2025 - Complete Guide",
                "snippet": f"Discover the best {query} that professionals recommend. Our comprehensive guide covers everything you need to know about {query}, including features, benefits, and expert tips."
            },
            {
                "title": f"Best {query.title()}: Expert Reviews and Comparisons",
                "snippet": f"Compare the top-rated {query} options available today. We've tested and reviewed dozens of {query} to help you make an informed decision."
            },
            {
                "title": f"Ultimate Guide to {query.title()} - Everything You Need to Know",
                "snippet": f"Learn everything about {query} in this detailed guide. From basics to advanced strategies, we cover all aspects of {query}."
            },
            {
                "title": f"{query.title()} 101: A Beginner's Guide",
                "snippet": f"New to {query}? This beginner-friendly guide explains the fundamentals of {query} and provides step-by-step instructions to get started."
            },
            {
                "title": f"How to Choose the Right {query.title()} for Your Needs",
                "snippet": f"Selecting the perfect {query} can be overwhelming. This article breaks down key factors to consider when choosing {query}."
            },
            {
                "title": f"{query.title()} Trends and Statistics 2025",
                "snippet": f"Stay updated with the latest trends in {query}. This report analyzes current market data and future predictions for {query}."
            },
            {
                "title": f"Professional Tips for Mastering {query.title()}",
                "snippet": f"Expert advice on getting the most out of {query}. Learn proven strategies and insider tips from industry professionals."
            },
            {
                "title": f"{query.title()} vs Alternatives: What's the Difference?",
                "snippet": f"Understanding the differences between {query} and similar options. This comparison helps you understand which solution fits your needs."
            },
            {
                "title": f"Common Mistakes to Avoid with {query.title()}",
                "snippet": f"Learn from others' mistakes. This article highlights common pitfalls when working with {query} and how to avoid them."
            },
            {
                "title": f"{query.title()} Best Practices: Industry Standards",
                "snippet": f"Follow industry best practices for {query}. This guide outlines standards and recommendations from leading experts in the field."
            }
        ]
        
        results = []
        for i, template in enumerate(mock_templates[:10], 1):
            domain = random.choice(["example.com", "guide.com", "review.com", "expert.com", "best.com"])
            results.append(SERPResult(
                rank=i,
                url=f"https://{domain}/{query.lower().replace(' ', '-')}",
                title=template["title"],
                snippet=template["snippet"]
            ))
        
        return results
    
    async def _fetch_serpapi(self, query: str, language: str) -> List[SERPResult]:
        """Fetch results from SerpAPI."""
        async with httpx.AsyncClient() as client:
            params = {
                "q": query,
                "api_key": self.api_key,
                "hl": language,
                "num": 10
            }
            response = await client.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "organic_results" in data:
                for item in data["organic_results"][:10]:
                    results.append(SERPResult(
                        rank=item.get("position", len(results) + 1),
                        url=item.get("link", ""),
                        title=item.get("title", ""),
                        snippet=item.get("snippet", "")
                    ))
            
            return results
    
    async def _fetch_dataforseo(self, query: str, language: str) -> List[SERPResult]:
        """Fetch results from DataForSEO (placeholder - implement based on their API)."""
        # Placeholder implementation
        # DataForSEO requires different authentication and endpoint structure
        return self._generate_mock_results(query, language)
    
    def analyze_themes(self, results: List[SERPResult]) -> List[str]:
        """
        Extract common themes and topics from SERP results.
        
        Args:
            results: List of SERP results
            
        Returns:
            List of identified themes/topics
        """
        # Simple keyword extraction from titles and snippets
        all_text = " ".join([r.title + " " + r.snippet for r in results])
        
        # Extract common words (excluding stop words)
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "should", "could", "may", "might", "must", "can", "this", "that", "these", "those"}
        
        words = all_text.lower().split()
        word_freq = {}
        for word in words:
            word = word.strip(".,!?;:()[]{}'\"")
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top themes
        sorted_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [theme[0] for theme in sorted_themes[:15]]

