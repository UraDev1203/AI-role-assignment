# SEO Article Generation API

A FastAPI-based backend service that generates SEO-optimized articles using AI and search engine results analysis.

## Features

- **SERP Analysis**: Analyzes top 10 search results to understand competitive landscape
- **Intelligent Content Generation**: Creates structured, SEO-optimized articles with proper heading hierarchy
- **Keyword Analysis**: Identifies and tracks primary and secondary keywords with density metrics
- **Internal Linking**: Suggests 3-5 relevant internal links with anchor text and placement context
- **External References**: Provides 2-4 authoritative sources with citation suggestions
- **FAQ Generation**: Creates FAQ sections based on common questions from search results
- **Job Management**: Asynchronous job processing with status tracking and persistence
- **SEO Validation**: Validates articles against SEO best practices
- **Durability**: Jobs are persisted and can be resumed if the process crashes

## Architecture

The system is built with:

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **OpenAI API**: AI-powered content generation (optional, falls back to templates)
- **SQLite**: Lightweight database for job persistence

## Project Structure

```
.
├── main.py                 # FastAPI application and routes
├── models.py               # Pydantic models for data validation
├── database.py             # Database models and setup
├── serp_service.py         # SERP analysis service
├── article_generator.py    # Article generation agent
├── job_service.py          # Job management service
├── requirements.txt        # Python dependencies
├── static/                 # Static files (web UI)
│   └── index.html         # Web interface
├── tests/                  # Test files
└── README.md              # This file
```

## Installation

1. **Clone the repository** (if applicable)

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (optional):
Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERP_API_KEY=your_serp_api_key_here
SERP_API_PROVIDER=serpapi  # or dataforseo, valueserp
```

Note: The system works without API keys using mock data for development.

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Or using Python directly:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Web UI

A simple web interface is included! Once the server is running, open your browser and navigate to:

**http://localhost:8000**

The UI allows you to:
- Enter topic/keyword
- Set target word count
- Select language (EN or FR)
- View real-time generation status
- See the complete generated article with all SEO metadata

The interface automatically polls the API to show progress and displays the full result when generation is complete.

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### POST `/generate`

Generate a new SEO-optimized article.

**Request Body**:
```json
{
  "topic": "best productivity tools for remote teams",
  "target_word_count": 1500,
  "language": "en"
}
```

**Response**:
```json
{
  "job_id": "uuid-here",
  "status": "pending",
  "message": "Article generation started. Use the job_id to check status."
}
```

### GET `/jobs/{job_id}`

Get the status of an article generation job.

**Response**:
```json
{
  "job_id": "uuid-here",
  "status": "running",
  "created_at": "2025-01-15T10:00:00",
  "completed_at": null,
  "error_message": null,
  "progress": {
    "stage": "generating_article",
    "themes_count": 12
  }
}
```

### GET `/jobs/{job_id}/result`

Get the complete article result for a completed job.

**Response**: See `ArticleResponse` model in `models.py` for full structure.

## Example Usage

### Using curl:

1. **Start article generation**:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "best productivity tools for remote teams",
    "target_word_count": 1500,
    "language": "en"
  }'
```

2. **Check job status**:
```bash
curl "http://localhost:8000/jobs/{job_id}"
```

3. **Get article result**:
```bash
curl "http://localhost:8000/jobs/{job_id}/result"
```

### Using Python:

```python
import requests
import time

# Start generation
response = requests.post("http://localhost:8000/generate", json={
    "topic": "best productivity tools for remote teams",
    "target_word_count": 1500,
    "language": "en"
})
job_id = response.json()["job_id"]

# Poll for completion
while True:
    status_response = requests.get(f"http://localhost:8000/jobs/{job_id}")
    status = status_response.json()["status"]
    
    if status == "completed":
        result = requests.get(f"http://localhost:8000/jobs/{job_id}/result")
        article = result.json()
        print(f"Article generated: {article['content']['title']}")
        break
    elif status == "failed":
        print(f"Generation failed: {status_response.json()['error_message']}")
        break
    
    time.sleep(2)
```

## Design Decisions

1. **Asynchronous Job Processing**: Articles are generated in background tasks to avoid long-running HTTP requests. This allows the API to handle multiple requests concurrently.

2. **Job Persistence**: All jobs are stored in SQLite database, allowing the system to resume jobs if it crashes after collecting SERP data.

3. **Mock Data Support**: The system can work without external API keys by using realistic mock data, making it easy to develop and test.

4. **Structured Data Models**: All data structures use Pydantic models for validation, type safety, and automatic API documentation.

5. **SEO Validation**: Built-in validation ensures generated articles meet SEO criteria (keyword density, meta tag lengths, heading structure, etc.).

6. **Graceful Degradation**: If OpenAI API is unavailable, the system falls back to template-based generation, ensuring it always produces output.

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Future Enhancements

- Real SERP API integration (SerpAPI, DataForSEO, ValueSERP)
- Content quality scoring with automatic revision triggers
- Enhanced FAQ generation from actual search result questions
- Support for multiple languages
- Caching of SERP results for similar queries
- Rate limiting and request throttling
- Authentication and API key management

## License

This project is part of a take-home assessment.

