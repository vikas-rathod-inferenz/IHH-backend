# Medical Assistant Backend

A comprehensive AI-powered medical chatbot backend built with **LangGraph**, **FastAPI**, **ChromaDB**, and multi-agent orchestration.

## 🌟 Features

- **🤖 Multi-Agent Architecture**: Specialized agents for RAG, web search, guardrails, and image analysis
- **📚 Advanced RAG System**: 
  - Query expansion with medical terminology
  - ChromaDB vector store for semantic search
  - Cross-encoder reranking for improved relevance
  - Confidence-based routing
- **🌐 Real-Time Web Search**: Tavily-powered search for latest medical research
- **🔒 Safety Guardrails**: Input/output validation for safe and appropriate responses
- **🔄 LangGraph Orchestration**: Sophisticated workflow management with human-in-the-loop
- **⚡ FastAPI Backend**: High-performance REST API with async support
- **📊 Confidence Scoring**: Intelligent routing based on response confidence

## 📁 Project Structure

```
medical_assistant_backend/
├── agents/
│   ├── guardrails/          # Input/output safety checks
│   ├── rag_agent/           # RAG agent with vector store
│   ├── web_search_agent/    # Web search integration
│   └── image_analysis_agent/ # Image analysis (placeholder)
├── core/
│   ├── orchestrator.py      # LangGraph workflow orchestration
│   └── state.py             # State definition for graph
├── utils/
│   ├── logger.py            # Logging configuration
│   └── models.py            # Pydantic models
├── data/                    # Data storage
├── uploads/                 # Uploaded documents
├── app.py                   # Main FastAPI application
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Azure OpenAI API access
- Tavily API key
- HuggingFace token

### Installation

1. **Clone or navigate to the project**
   ```bash
   cd d:\IHH\medical_assistant_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

## 📝 API Endpoints

### Chat
```http
POST /chat
Content-Type: application/json

{
  "question": "What are the symptoms of diabetes?",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id",
  "use_expansion": true,
  "use_reranking": true
}
```

### Upload Document
```http
POST /documents/upload
Content-Type: multipart/form-data

file: <your_document.pdf>
```

### Health Check
```http
GET /health
```

### Collection Info
```http
GET /documents/collection-info
```

## 🔧 Configuration

Key configuration options in `.env`:

```env
# LLM Configuration
OPENAI_API_KEY=your_api_key
AZURE_ENDPOINT=your_endpoint
MODEL_NAME=gpt-4o

# Embedding Model
EMBEDDING_API_KEY=your_embedding_key
EMBEDDING_MODEL_NAME=text-embedding-ada-002

# Web Search
TAVILY_API_KEY=your_tavily_key

# HuggingFace (for reranking)
HUGGINGFACE_TOKEN=your_hf_token

# RAG Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
RERANK_TOP_K=3
CONFIDENCE_THRESHOLD=0.7
```

## 🎯 Workflow

The system uses LangGraph to orchestrate the following workflow:

1. **Input Validation**: Guardrails check for safety and medical relevance
2. **Agent Decision**: Routes to appropriate agent(s)
3. **RAG Agent**: Retrieves from knowledge base with query expansion and reranking
4. **Confidence Check**: If confidence < threshold, routes to web search
5. **Web Search Agent**: Searches latest medical research (if needed)
6. **Combine Results**: Merges information from multiple sources
7. **Output Validation**: Safety checks on generated response
8. **Human Review**: Flags low-confidence responses (human-in-the-loop)
9. **Finalize**: Returns complete response

## 🔍 RAG Pipeline

1. **Query Expansion**: LLM expands query with medical synonyms
2. **Vector Search**: ChromaDB semantic similarity search
3. **Reranking**: Cross-encoder model reranks results
4. **Confidence Scoring**: Calculates confidence based on relevance scores
5. **Response Generation**: LLM generates response with context

## 🛡️ Safety Features

- **Input Guardrails**: Detects emergencies, inappropriate content, off-topic queries
- **Output Guardrails**: Ensures medical disclaimers, balanced information
- **Confidence Thresholds**: Routes to web search or human review when uncertain
- **Human-in-the-Loop**: Expert validation for critical responses

## 📊 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

Example CURL request:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the symptoms of diabetes?",
    "use_expansion": true,
    "use_reranking": true
  }'
```

## 📚 Adding Documents

To populate the knowledge base:

1. Use the `/documents/upload` endpoint
2. Or directly add documents to vector store:
   ```python
   from agents.rag_agent import get_vector_store, get_document_processor
   
   processor = get_document_processor()
   chunks = processor.process_text(text, metadata)
   
   vector_store = get_vector_store()
   vector_store.add_documents(chunks)
   ```

## 🔄 Human-in-the-Loop

The system flags responses for human review when:
- Confidence score < threshold (default 0.7)
- Complex medical queries requiring expert validation
- Potential edge cases or ambiguous queries

## 🎨 Extending the System

### Adding New Agents

1. Create agent module in `agents/` directory
2. Implement agent class with `query()` method
3. Add node to LangGraph in `core/orchestrator.py`
4. Update routing logic

### Custom Guardrails

Edit `agents/guardrails/guardrails.py` to add custom safety checks.

## 🐛 Troubleshooting

**Issue**: ChromaDB initialization error
- Solution: Ensure `data/chroma_db` directory exists and has write permissions

**Issue**: Out of memory during reranking
- Solution: Reduce `TOP_K_RETRIEVAL` in config

**Issue**: Slow response times
- Solution: Disable query expansion or reranking for faster responses

## 📄 License

This project is based on the reference architecture from [Medical-Assistant-with-LangGraph](https://github.com/christopherth1006/Medical-Assistant-with-LangGraph).

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Image analysis agent implementation
- PubMed search integration
- Enhanced human-in-the-loop interface
- Additional medical knowledge sources
- Performance optimizations

## 📧 Support

For issues and questions, please check:
- API documentation at `/docs`
- Logs in `logs/` directory
- Configuration in `config.py`
