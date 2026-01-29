# Medical Assistant Backend - Quick Start Guide

## Setup Steps

### 1. Install Python Dependencies

```bash
cd d:\IHH\medical_assistant_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
copy .env.example .env
```

Required API keys:
- **Azure OpenAI**: Get from Azure Portal
- **Tavily**: Sign up at https://tavily.com
- **HuggingFace**: Get token from https://huggingface.co/settings/tokens

### 3. Start the Server

```bash
python app.py
```

Or with uvicorn:
```bash
uvicorn app:app --reload --port 8000
```

### 4. Test the API

Open browser to `http://localhost:8000/docs` for interactive API documentation.

Or use curl:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is diabetes?\"}"
```

## Key Endpoints

- `POST /chat` - Ask medical questions
- `POST /documents/upload` - Upload documents to knowledge base
- `GET /health` - Check system health
- `GET /documents/collection-info` - View document count

## Architecture Flow

1. User question → Input guardrails
2. Route to RAG agent (knowledge base)
3. If low confidence → Web search agent
4. Combine results
5. Output guardrails
6. Return response with sources

## Configuration

Edit `.env` to customize:
- `CONFIDENCE_THRESHOLD` - When to trigger web search (default: 0.7)
- `TOP_K_RETRIEVAL` - Number of documents to retrieve (default: 5)
- `CHUNK_SIZE` - Document chunk size (default: 1000)

## Adding Documents

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@your_document.pdf"
```

## Troubleshooting

**Q: Server won't start**
- Check all API keys in `.env`
- Ensure port 8000 is available
- Check logs in `logs/` directory

**Q: No responses from RAG**
- Upload documents first using `/documents/upload`
- Check collection count at `/documents/collection-info`

**Q: Slow responses**
- Disable reranking: `"use_reranking": false` in request
- Reduce `TOP_K_RETRIEVAL` in `.env`

## Next Steps

1. Upload medical documents to build knowledge base
2. Test with various medical queries
3. Monitor confidence scores and agent routing
4. Adjust thresholds based on performance
5. Implement human-in-the-loop review system
