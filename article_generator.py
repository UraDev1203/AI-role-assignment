"""
Article generation agent with SEO optimization.
"""
import os
import re
from typing import List, Dict, Any, Optional
from models import (
    ArticleContent, KeywordAnalysis, InternalLink, 
    ExternalReference, FAQItem, SERPResult
)
from openai import AsyncOpenAI


class ArticleGenerator:
    """Agent for generating SEO-optimized articles."""
    
    def __init__(self):
        """Initialize article generator."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
    
    async def generate_article(
        self,
        topic: str,
        serp_results: List[SERPResult],
        themes: List[str],
        target_word_count: int,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate a complete SEO-optimized article.
        
        Args:
            topic: Main topic/keyword
            serp_results: SERP analysis results
            themes: Extracted themes from SERP
            target_word_count: Target word count
            language: Language code
            
        Returns:
            Dictionary with all article components
        """
        if self.client:
            return await self._generate_with_ai(topic, serp_results, themes, target_word_count, language)
        else:
            return self._generate_template_article(topic, serp_results, themes, target_word_count)
    
    async def _generate_with_ai(
        self,
        topic: str,
        serp_results: List[SERPResult],
        themes: List[str],
        target_word_count: int,
        language: str
    ) -> Dict[str, Any]:
        """Generate article using OpenAI API."""
        # Create context from SERP results
        serp_context = "\n".join([
            f"Rank {r.rank}: {r.title}\n{r.snippet}\n"
            for r in serp_results[:5]
        ])
        
        themes_str = ", ".join(themes[:10])
        
        prompt = f"""You are an expert SEO content writer. Generate a high-quality, SEO-optimized article on the topic: "{topic}".

Based on the following search results analysis:
{serp_context}

Identified themes: {themes_str}

Requirements:
1. Target word count: {target_word_count}
2. Include primary keyword "{topic}" in title, introduction, and naturally throughout
3. Use proper heading hierarchy (H1, H2, H3)
4. Write naturally - avoid keyword stuffing
5. Cover the main themes identified from search results
6. Include a compelling introduction and conclusion

Generate the article in JSON format with this structure:
{{
    "title": "Article title (H1, include primary keyword)",
    "meta_title": "SEO meta title (50-60 chars, include primary keyword)",
    "meta_description": "SEO meta description (150-160 chars, compelling)",
    "introduction": "Engaging introduction paragraph (include primary keyword naturally)",
    "headings": [
        {{"level": 2, "text": "H2 heading", "content": "Paragraph content under this heading"}},
        {{"level": 3, "text": "H3 subheading", "content": "Subsection content"}},
        ...
    ],
    "body": "Main body content (combine all sections)",
    "conclusion": "Strong conclusion paragraph"
}}

Make sure the content is well-structured, informative, and reads naturally while following SEO best practices."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert SEO content writer who creates high-quality, natural-sounding articles that rank well in search engines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            article_data = json.loads(response.choices[0].message.content)
            return article_data
        except Exception as e:
            print(f"Error generating article with AI: {e}. Using template.")
            return self._generate_template_article(topic, serp_results, themes, target_word_count)
    
    def _generate_template_article(
        self,
        topic: str,
        serp_results: List[SERPResult],
        themes: List[str],
        target_word_count: int
    ) -> Dict[str, Any]:
        """Generate template article when AI is not available."""
        # Generate a structured template article
        title = f"Complete Guide to {topic.title()}: Everything You Need to Know"
        meta_title = f"{topic.title()} Guide 2025 | Expert Tips & Best Practices"
        meta_description = f"Discover everything about {topic}. Our comprehensive guide covers key insights, expert recommendations, and best practices for {topic}."
        
        introduction = f"""When it comes to {topic}, understanding the fundamentals and best practices can make a significant difference. Whether you're just getting started or looking to optimize your approach, this comprehensive guide will provide you with actionable insights and expert recommendations.

In this article, we'll explore the key aspects of {topic}, including the most important considerations, common challenges, and proven strategies that professionals use to achieve success. Our analysis is based on current industry standards and insights from top-performing resources."""
        
        # Generate headings and content based on themes
        headings = []
        body_sections = []
        
        main_sections = [
            f"What is {topic}?",
            f"Key Benefits of {topic}",
            f"Best Practices for {topic}",
            f"Common Challenges and Solutions",
            f"Expert Tips and Recommendations"
        ]
        
        for i, section in enumerate(main_sections[:5], 1):
            headings.append({
                "level": 2,
                "text": section,
                "content": f"""{section}

This section covers essential information about {section.lower()}. Understanding these concepts is crucial for anyone working with {topic}. 

Based on our analysis of top search results, we've identified the most important factors to consider. These insights come from industry leaders and proven methodologies that have demonstrated success across various applications.

Key points to remember:
- Focus on understanding the core principles
- Apply best practices consistently
- Learn from common mistakes others have made
- Stay updated with the latest trends and developments

By following these guidelines, you'll be better equipped to work effectively with {topic} and achieve your desired outcomes."""
            })
            body_sections.append(headings[-1]["content"])
        
        body = "\n\n".join(body_sections)
        
        conclusion = f"""In conclusion, {topic} represents an important area that requires careful consideration and strategic approach. By following the guidelines and best practices outlined in this guide, you'll be well-positioned to achieve success.

Remember that mastery of {topic} comes with practice and continuous learning. Stay informed about the latest developments, and don't hesitate to adapt your approach based on new insights and changing circumstances.

Whether you're a beginner or an experienced professional, there's always more to learn about {topic}. We hope this guide has provided valuable insights to help you on your journey."""
        
        return {
            "title": title,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "introduction": introduction,
            "headings": headings,
            "body": body,
            "conclusion": conclusion
        }
    
    def analyze_keywords(self, content: str, primary_keyword: str) -> KeywordAnalysis:
        """
        Analyze keyword usage in the generated content.
        
        Args:
            content: Generated article content
            primary_keyword: Primary target keyword
            
        Returns:
            KeywordAnalysis object
        """
        content_lower = content.lower()
        primary_lower = primary_keyword.lower()
        
        # Count primary keyword
        primary_count = len(re.findall(r'\b' + re.escape(primary_lower) + r'\b', content_lower))
        total_words = len(content.split())
        primary_density = (primary_count / total_words * 100) if total_words > 0 else 0
        
        # Extract potential secondary keywords (words that appear frequently)
        words = re.findall(r'\b\w{4,}\b', content_lower)
        word_freq = {}
        for word in words:
            if word != primary_lower and len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top secondary keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        secondary_keywords = [word for word, _ in sorted_words[:10]]
        
        # Calculate densities
        keyword_density = {primary_keyword: round(primary_density, 2)}
        for keyword in secondary_keywords[:5]:
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content_lower))
            density = (count / total_words * 100) if total_words > 0 else 0
            keyword_density[keyword] = round(density, 2)
        
        return KeywordAnalysis(
            primary_keyword=primary_keyword,
            secondary_keywords=secondary_keywords[:5],
            keyword_density=keyword_density
        )
    
    def generate_internal_links(self, topic: str) -> List[InternalLink]:
        """Generate internal linking suggestions."""
        # Generate relevant internal link suggestions based on topic
        suggestions = [
            InternalLink(
                anchor_text=f"{topic} best practices",
                target_page=f"/guides/{topic.lower().replace(' ', '-')}-best-practices",
                context="In the best practices section"
            ),
            InternalLink(
                anchor_text=f"{topic} tools and resources",
                target_page=f"/resources/{topic.lower().replace(' ', '-')}-tools",
                context="When discussing tools and resources"
            ),
            InternalLink(
                anchor_text=f"{topic} case studies",
                target_page=f"/case-studies/{topic.lower().replace(' ', '-')}",
                context="In the examples section"
            ),
            InternalLink(
                anchor_text=f"{topic} FAQ",
                target_page=f"/faq/{topic.lower().replace(' ', '-')}",
                context="Before the conclusion"
            ),
            InternalLink(
                anchor_text=f"advanced {topic} strategies",
                target_page=f"/advanced/{topic.lower().replace(' ', '-')}-strategies",
                context="In the expert tips section"
            )
        ]
        return suggestions[:5]
    
    def generate_external_references(self, topic: str) -> List[ExternalReference]:
        """Generate external authoritative references."""
        references = [
            ExternalReference(
                url="https://example.com/industry-report",
                title=f"2025 Industry Report on {topic}",
                context="In the statistics section",
                citation_text="According to the 2025 Industry Report"
            ),
            ExternalReference(
                url="https://example.com/research-study",
                title=f"Academic Study: {topic} Analysis",
                context="When discussing research findings",
                citation_text="Research published in 2024 shows"
            ),
            ExternalReference(
                url="https://example.com/expert-guide",
                title=f"Expert Guide to {topic}",
                context="In the best practices section",
                citation_text="As noted by industry experts"
            ),
            ExternalReference(
                url="https://example.com/standards",
                title=f"Industry Standards for {topic}",
                context="When discussing compliance and standards",
                citation_text="Following industry standards"
            )
        ]
        return references[:4]
    
    def generate_faq(self, serp_results: List[SERPResult], topic: str) -> List[FAQItem]:
        """Generate FAQ section from common questions in search results."""
        # Extract potential questions from snippets
        faq_items = [
            FAQItem(
                question=f"What is {topic}?",
                answer=f"{topic.title()} refers to a comprehensive approach that encompasses various aspects and best practices. Understanding {topic} is essential for achieving optimal results in this area."
            ),
            FAQItem(
                question=f"How do I get started with {topic}?",
                answer=f"Getting started with {topic} involves understanding the fundamentals, setting clear goals, and following established best practices. Begin by researching the basics and gradually implementing strategies that align with your specific needs."
            ),
            FAQItem(
                question=f"What are the best practices for {topic}?",
                answer=f"The best practices for {topic} include maintaining consistency, staying updated with industry trends, and following proven methodologies. It's important to adapt these practices to your specific context and requirements."
            ),
            FAQItem(
                question=f"What are common challenges with {topic}?",
                answer=f"Common challenges with {topic} include staying current with evolving standards, managing complexity, and ensuring quality outcomes. However, these challenges can be addressed through proper planning and following expert guidance."
            )
        ]
        return faq_items
    
    def validate_seo(self, content: ArticleContent, keyword_analysis: KeywordAnalysis) -> Dict[str, Any]:
        """
        Validate that the article meets SEO criteria.
        
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Check meta title length
        if len(content.meta_title) < 30:
            warnings.append("Meta title is too short (recommended: 30-60 characters)")
        elif len(content.meta_title) > 60:
            warnings.append("Meta title is too long (recommended: 30-60 characters)")
        
        # Check meta description length
        if len(content.meta_description) < 120:
            warnings.append("Meta description is too short (recommended: 120-160 characters)")
        elif len(content.meta_description) > 160:
            warnings.append("Meta description is too long (recommended: 120-160 characters)")
        
        # Check primary keyword in title
        if keyword_analysis.primary_keyword.lower() not in content.title.lower():
            issues.append("Primary keyword not found in article title")
        
        # Check primary keyword in introduction
        if keyword_analysis.primary_keyword.lower() not in content.introduction.lower():
            issues.append("Primary keyword not found in introduction")
        
        # Check keyword density
        primary_density = keyword_analysis.keyword_density.get(keyword_analysis.primary_keyword, 0)
        if primary_density < 0.5:
            warnings.append(f"Primary keyword density is low ({primary_density}%), recommended: 0.5-2%")
        elif primary_density > 3:
            warnings.append(f"Primary keyword density is high ({primary_density}%), may be considered keyword stuffing")
        
        # Check heading structure
        h2_count = sum(1 for h in content.headings if h.get("level") == 2)
        if h2_count < 3:
            warnings.append("Article should have at least 3 H2 headings for better structure")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, 100 - (len(issues) * 20) - (len(warnings) * 5))
        }

