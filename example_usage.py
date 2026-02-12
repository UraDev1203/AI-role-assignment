"""
Example usage of the SEO Article Generation API.
"""
import requests
import time
import json


def generate_article_example():
    """Example of generating an article."""
    base_url = "http://localhost:8000"
    
    # Step 1: Start article generation
    print("Starting article generation...")
    response = requests.post(f"{base_url}/generate", json={
        "topic": "best productivity tools for remote teams",
        "target_word_count": 1500,
        "language": "en"
    })
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    
    job_data = response.json()
    job_id = job_data["job_id"]
    print(f"Job created: {job_id}")
    print(f"Status: {job_data['status']}\n")
    
    # Step 2: Poll for job completion
    print("Waiting for article generation to complete...")
    max_wait = 300  # 5 minutes max
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status_response = requests.get(f"{base_url}/jobs/{job_id}")
        
        if status_response.status_code != 200:
            print(f"Error checking status: {status_response.status_code}")
            break
        
        status_data = status_response.json()
        status = status_data["status"]
        progress = status_data.get("progress", {})
        
        print(f"Status: {status}", end="")
        if progress:
            stage = progress.get("stage", "unknown")
            print(f" | Stage: {stage}", end="")
            if "word_count" in progress:
                print(f" | Words: {progress['word_count']}", end="")
            if "seo_score" in progress:
                print(f" | SEO Score: {progress['seo_score']}", end="")
        print()
        
        if status == "completed":
            print("\nArticle generation completed!")
            break
        elif status == "failed":
            print(f"\nArticle generation failed: {status_data.get('error_message', 'Unknown error')}")
            return
        
        time.sleep(2)
    
    # Step 3: Get the article result
    print("\nFetching article result...")
    result_response = requests.get(f"{base_url}/jobs/{job_id}/result")
    
    if result_response.status_code != 200:
        print(f"Error fetching result: {result_response.status_code} - {result_response.text}")
        return
    
    article = result_response.json()
    
    # Display article information
    print("\n" + "="*80)
    print("ARTICLE GENERATED SUCCESSFULLY")
    print("="*80)
    print(f"\nTopic: {article['topic']}")
    print(f"Word Count: {article['word_count']}")
    print(f"Status: {article['status']}")
    
    if article.get("content"):
        content = article["content"]
        print(f"\nTitle: {content['title']}")
        print(f"\nMeta Title: {content['meta_title']}")
        print(f"\nMeta Description: {content['meta_description']}")
        print(f"\nIntroduction:\n{content['introduction']}")
        print(f"\nConclusion:\n{content['conclusion']}")
    
    if article.get("keyword_analysis"):
        ka = article["keyword_analysis"]
        print(f"\nPrimary Keyword: {ka['primary_keyword']}")
        print(f"Secondary Keywords: {', '.join(ka['secondary_keywords'][:5])}")
        print(f"Keyword Density: {ka['keyword_density']}")
    
    if article.get("internal_links"):
        print(f"\nInternal Links ({len(article['internal_links'])}):")
        for link in article["internal_links"]:
            print(f"  - {link['anchor_text']} -> {link['target_page']}")
    
    if article.get("external_references"):
        print(f"\nExternal References ({len(article['external_references'])}):")
        for ref in article["external_references"]:
            print(f"  - {ref['title']}: {ref['url']}")
    
    if article.get("faq_section"):
        print(f"\nFAQ Section ({len(article['faq_section'])} questions):")
        for faq in article["faq_section"]:
            print(f"  Q: {faq['question']}")
            print(f"  A: {faq['answer']}\n")
    
    print("="*80)
    
    # Save to file
    with open("generated_article.json", "w", encoding="utf-8") as f:
        json.dump(article, f, indent=2, ensure_ascii=False, default=str)
    print("\nArticle saved to generated_article.json")


if __name__ == "__main__":
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Start it with: uvicorn main:app --reload\n")
    generate_article_example()

