# Medical Assistant Backend - Complete Setup & Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Populating Knowledge Base](#populating-knowledge-base)
6. [Testing](#testing)
7. [Docker Deployment](#docker-deployment)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)

### API Keys Required
1. **Azure OpenAI**
   - Get from: [Azure Portal](https://portal.azure.com)
   - Required for: LLM and embeddings
   
2. **Tavily API**
   - Get from: [Tavily](https://tavily.com)
   - Required for: Web search functionality
   
3. **HuggingFace Token**
   - Get from: [HuggingFace](https://huggingface.co/settings/tokens)
   - Required for: Document reranking

4. **LangSmith** (Optional)
   - Get from: [LangSmith](https://smith.langchain.com)
   - Required for: Tracing and monitoring

## Local Development Setup

### Step 1: Navigate to Project Directory
```bash
cd d:\IHH\medical_assistant_backend
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables
```bash
# Copy example environment file
copy .env.example .env

# Edit .env file with your API keys
notepad .env
```

Update the following in `.env`:
```env
# Azure OpenAI Configuration
OPENAI_API_KEY=your_azure_openai_key_here
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
MODEL_NAME=gpt-4o
DEPLOYMENT_NAME=gpt-4o

# Embedding Configuration
EMBEDDING_API_KEY=your_embedding_key_here
EMBEDDING_AZURE_ENDPOINT=https://your-resource.openai.azure.com/
EMBEDDING_MODEL_NAME=text-embedding-ada-002

# Web Search
TAVILY_API_KEY=your_tavily_key_here

# HuggingFace
HUGGINGFACE_TOKEN=your_hf_token_here

# Optional: LangSmith
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=your_langsmith_key_here
```

## Configuration

### Key Settings in `.env`

#### Application Settings
```env
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

#### RAG Settings
```env
CHUNK_SIZE=1000          # Size of text chunks
CHUNK_OVERLAP=200        # Overlap between chunks
TOP_K_RETRIEVAL=5        # Number of documents to retrieve
RERANK_TOP_K=3          # Number after reranking
CONFIDENCE_THRESHOLD=0.7 # Threshold for web search fallback
```

#### File Upload Settings
```env
MAX_UPLOAD_SIZE=10485760              # 10MB in bytes
ALLOWED_EXTENSIONS=pdf,txt,docx,png,jpg,jpeg
```

## Running the Application

### Option 1: Using Python Directly
```bash
python app.py
```

### Option 2: Using Uvicorn
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: With Custom Settings
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

### Access the Application
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Populating Knowledge Base

### Method 1: Add Sample Medical Data
```bash
python ingest_documents.py --sample
```

This will add sample documents about:
- Diabetes
- Hypertension
- Common Cold vs Flu

### Method 2: Ingest from Directory
```bash
python ingest_documents.py --directory "path/to/your/documents" --patterns "*.txt" "*.md"
```

### Method 3: Upload via API
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

### Method 4: Programmatically
```python
from agents.rag_agent import get_vector_store, get_document_processor

processor = get_document_processor()
vector_store = get_vector_store()

# Process and add text
chunks = processor.process_text(
    text="Your medical content here",
    metadata={"source": "medical_guide.txt"}
)
vector_store.add_documents(chunks)
```

## Testing

### 1. Run Test Suite
```bash
python test_api.py
```

### 2. Manual API Testing

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Chat Request
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What are the symptoms of diabetes?\"}"
```

#### Collection Info
```bash
curl http://localhost:8000/documents/collection-info
```

### 3. Interactive Testing
Visit `http://localhost:8000/docs` for interactive Swagger UI

## Docker Deployment

### Build Docker Image
```bash
docker build -t medical-assistant-backend .
```

### Run with Docker
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e AZURE_ENDPOINT=your_endpoint \
  -e TAVILY_API_KEY=your_key \
  -e HUGGINGFACE_TOKEN=your_token \
  -v $(pwd)/data:/app/data \
  medical-assistant-backend
```

### Using Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Deployment

### 1. Environment Configuration
Create production `.env`:
```env
DEBUG=False
LOG_LEVEL=WARNING
CONFIDENCE_THRESHOLD=0.75
```

### 2. Use Production Server
Install gunicorn:
```bash
pip install gunicorn
```

Run with gunicorn:
```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. Behind Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4. Systemd Service
Create `/etc/systemd/system/medical-assistant.service`:
```ini
[Unit]
Description=Medical Assistant Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/medical_assistant_backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start medical-assistant
sudo systemctl enable medical-assistant
```

## Troubleshooting

### Issue: Module not found errors
**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: ChromaDB initialization fails
**Solution:**
```bash
# Ensure directory exists
mkdir -p data/chroma_db

# Check permissions
chmod 755 data/chroma_db
```

### Issue: Out of memory during reranking
**Solution:**
Edit `.env`:
```env
TOP_K_RETRIEVAL=3
RERANK_TOP_K=2
```

### Issue: Slow response times
**Solution:**
1. Disable query expansion:
```json
{
  "question": "your question",
  "use_expansion": false
}
```

2. Reduce retrieval count in `.env`:
```env
TOP_K_RETRIEVAL=3
```

### Issue: API key errors
**Solution:**
1. Verify keys in `.env`
2. Check Azure endpoint format
3. Ensure API keys have proper permissions

### Issue: No documents retrieved
**Solution:**
1. Check collection count:
```bash
curl http://localhost:8000/documents/collection-info
```

2. Add sample data:
```bash
python ingest_documents.py --sample
```

### Issue: Port already in use
**Solution:**
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## Monitoring

### View Logs
```bash
# Application logs
tail -f logs/medical_assistant.log

# Error logs
tail -f logs/errors.log
```

### Check System Health
```bash
curl http://localhost:8000/health
```

### Monitor with LangSmith
If enabled, visit [LangSmith](https://smith.langchain.com) to view traces

## Performance Optimization

1. **Enable Caching**: Implement Redis for response caching
2. **Load Balancing**: Use multiple workers with gunicorn
3. **Database Optimization**: Use persistent ChromaDB server
4. **API Rate Limiting**: Implement rate limiting for production

## Security Considerations

1. **API Key Management**: Use secrets manager in production
2. **CORS Configuration**: Restrict origins in production
3. **HTTPS**: Always use HTTPS in production
4. **Input Validation**: Already implemented via guardrails
5. **Rate Limiting**: Implement per-user rate limits

## Backup and Maintenance

### Backup Vector Database
```bash
# Backup ChromaDB
cp -r data/chroma_db data/chroma_db_backup_$(date +%Y%m%d)
```

### Clear Collection (Careful!)
```bash
curl -X DELETE http://localhost:8000/documents/collection
```

## Support

For issues:
1. Check logs in `logs/` directory
2. Verify configuration in `.env`
3. Review API documentation at `/docs`
4. Check system health at `/health`
