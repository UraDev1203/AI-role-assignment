# Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up environment variables:
Create a `.env` file with:
```
OPENAI_API_KEY=your_key_here
SERP_API_KEY=your_key_here
```

## Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Quick Test

1. **Generate an article**:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "best productivity tools", "target_word_count": 1500}'
```

2. **Check status** (use the job_id from step 1):
```bash
curl "http://localhost:8000/jobs/{job_id}"
```

3. **Get result** (when status is "completed"):
```bash
curl "http://localhost:8000/jobs/{job_id}/result"
```

## Using Python Example

Run the example script:
```bash
python example_usage.py
```

Make sure the server is running first!

## Running Tests

```bash
pytest tests/
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

