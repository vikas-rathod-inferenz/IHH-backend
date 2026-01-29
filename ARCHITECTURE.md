# Medical Assistant Backend - Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                          │
│                     (app.py - Port 8000)                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                        │
│                   (core/orchestrator.py)                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Input       │→ │   Agent      │→ │  Output      │         │
│  │  Validation  │  │  Decision    │  │  Validation  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Guardrails  │  │  RAG Agent   │  │  Human       │         │
│  │              │  │  Web Search  │  │  Review      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                ▼                ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   ChromaDB       │  │  Azure OpenAI    │  │  Tavily Search   │
│  Vector Store    │  │  - LLM (GPT-4o)  │  │  Web API         │
│  - Embeddings    │  │  - Embeddings    │  │                  │
│  - Similarity    │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## 📊 Component Breakdown

### 1. API Layer (FastAPI)
**File:** `app.py`
- RESTful API endpoints
- Request/response validation
- CORS middleware
- Exception handling
- Health checks

**Endpoints:**
- `POST /chat` - Main chat interface
- `POST /documents/upload` - Document upload
- `GET /health` - Health check
- `GET /documents/collection-info` - Collection status

### 2. Orchestration Layer (LangGraph)
**File:** `core/orchestrator.py`
**State:** `core/state.py`

**Workflow Nodes:**
1. **Input Validation** - Guardrails check
2. **Agent Decision** - Route selection
3. **RAG Agent** - Knowledge base retrieval
4. **Web Search Agent** - Online research
5. **Combine Results** - Multi-source synthesis
6. **Output Validation** - Safety checks
7. **Human Review** - Expert validation (low confidence)
8. **Finalize** - Response preparation

**Routing Logic:**
- Input valid → Agent Decision
- RAG confidence high → Output Validation
- RAG confidence low → Web Search
- Output flagged → Human Review

### 3. Agent Layer

#### a) Guardrails Agent
**File:** `agents/guardrails/guardrails.py`

**Input Validation:**
- Medical relevance check
- Emergency detection
- Inappropriate content filtering
- Safety screening

**Output Validation:**
- Medical accuracy review
- Disclaimer verification
- Harm prevention
- Bias detection

#### b) RAG Agent
**Files:** `agents/rag_agent/`

**Components:**
- **Vector Store** (`vector_store.py`)
  - ChromaDB integration
  - Embedding management
  - Similarity search
  - MMR search
  
- **Query Expander** (`query_expander.py`)
  - Medical term expansion
  - Synonym generation
  - Context enrichment
  
- **Reranker** (`reranker.py`)
  - Cross-encoder scoring
  - Relevance reranking
  - HuggingFace models
  
- **RAG Agent** (`rag_agent.py`)
  - Pipeline orchestration
  - Confidence calculation
  - Response generation

**RAG Pipeline:**
```
Query → Expand → Retrieve → Rerank → Generate → Score
```

#### c) Web Search Agent
**Files:** `agents/web_search_agent/`

**Components:**
- **Tavily Search** (`tavily_search.py`)
  - Medical domain search
  - Source filtering
  - Result ranking
  
- **Web Search Agent** (`web_search_agent.py`)
  - Search execution
  - Result synthesis
  - Source citation

#### d) Image Analysis Agent (Placeholder)
**Files:** `agents/image_analysis_agent/`
- Brain tumor detection (future)
- Chest X-ray analysis (future)
- Skin lesion segmentation (future)

### 4. Data Layer

#### ChromaDB Vector Store
**Location:** `data/chroma_db/`
- Persistent storage
- Document embeddings
- Metadata indexing
- Collection management

#### Document Processing
**Component:** `DocumentProcessor`
- Text chunking (1000 chars)
- Overlap management (200 chars)
- Metadata attachment
- Batch processing

### 5. Utility Layer

#### Configuration
**File:** `config.py`
- Environment variables
- Settings management
- Path configuration
- API key management

#### Logging
**File:** `utils/logger.py`
- Structured logging
- Rotating file handlers
- Console output
- Error tracking

#### Models
**File:** `utils/models.py`
- Pydantic schemas
- Request validation
- Response formatting
- Type safety

## 🔄 Request Flow

### Standard Chat Request

```
1. User sends POST /chat with question
   ↓
2. FastAPI receives and validates request
   ↓
3. Orchestrator initializes state
   ↓
4. Input Validation Node
   - Guardrails check input
   - Classify query type
   - Detect emergencies
   ↓
5. Agent Decision Node
   - Determine agent routing
   - Start with RAG agent
   ↓
6. RAG Agent Node
   - Expand query with medical terms
   - Retrieve documents from ChromaDB
   - Rerank with cross-encoder
   - Calculate confidence score
   ↓
7. Confidence Check
   - If confidence ≥ threshold → Output Validation
   - If confidence < threshold → Web Search Agent
   ↓
8. Web Search Agent Node (if needed)
   - Search Tavily for recent research
   - Filter medical sources
   - Synthesize findings
   ↓
9. Combine Results Node
   - Merge RAG + Web Search
   - Aggregate sources
   - Calculate combined confidence
   ↓
10. Output Validation Node
    - Guardrails check output
    - Add disclaimers if needed
    - Flag for human review if low confidence
    ↓
11. Human Review Node (if flagged)
    - Add review notice
    - Mark for expert validation
    ↓
12. Finalize Node
    - Prepare final response
    - Attach metadata
    - Calculate processing time
    ↓
13. Return response to user
```

## 🎯 Key Features

### 1. Multi-Agent Orchestration
- **LangGraph** manages complex workflows
- State-based execution
- Conditional routing
- Error recovery

### 2. Advanced RAG
- **Query Expansion** - Medical terminology
- **Hybrid Retrieval** - Semantic + keyword
- **Reranking** - Cross-encoder scoring
- **Confidence** - Quality assessment

### 3. Safety & Compliance
- **Input Guardrails** - Pre-screening
- **Output Guardrails** - Post-validation
- **Human-in-the-Loop** - Expert oversight
- **Medical Disclaimers** - Legal protection

### 4. Intelligent Routing
- **Confidence-Based** - Automatic fallback
- **Multi-Source** - RAG + Web Search
- **Context-Aware** - Emergency detection
- **Optimized** - Minimal latency

## 📈 Scalability Considerations

### Horizontal Scaling
- Stateless FastAPI instances
- Load balancer distribution
- Shared ChromaDB instance
- Distributed caching

### Vertical Scaling
- GPU acceleration for reranking
- Larger vector dimensions
- More workers per instance
- Increased memory allocation

### Performance Optimization
- Response caching (Redis)
- Batch embedding generation
- Async operations
- Connection pooling

## 🔐 Security Features

### Authentication & Authorization
- API key validation (to be added)
- User session management
- Rate limiting (to be added)

### Data Protection
- Encrypted connections (HTTPS)
- Secure API key storage
- Input sanitization
- Output filtering

### Compliance
- HIPAA considerations
- Medical disclaimer requirements
- Data retention policies
- Audit logging

## 🧪 Testing Strategy

### Unit Tests
- Individual agent testing
- Component isolation
- Mock external APIs

### Integration Tests
- End-to-end workflows
- Multi-agent coordination
- API endpoint testing

### Load Tests
- Concurrent requests
- Response time monitoring
- Resource utilization

## 📚 Technology Stack

### Core Framework
- **FastAPI** - Web framework
- **LangGraph** - Workflow orchestration
- **LangChain** - LLM integration

### AI/ML
- **Azure OpenAI** - GPT-4o (LLM)
- **ChromaDB** - Vector database
- **HuggingFace** - Reranking models
- **Sentence Transformers** - Embeddings

### Search & Retrieval
- **Tavily** - Web search API
- **BM25** - Keyword search
- **Cross-Encoder** - Reranking

### Utilities
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Python-dotenv** - Config management

## 🎓 Key Design Patterns

1. **Repository Pattern** - Vector store abstraction
2. **Factory Pattern** - Agent instantiation
3. **Strategy Pattern** - Routing logic
4. **Observer Pattern** - Logging & monitoring
5. **Chain of Responsibility** - Workflow nodes

## 🚀 Future Enhancements

1. **Image Analysis Agent** - Medical imaging support
2. **PubMed Integration** - Direct research access
3. **Multi-Modal RAG** - Text + images
4. **Streaming Responses** - Real-time output
5. **Advanced Caching** - Redis integration
6. **User Management** - Authentication system
7. **Analytics Dashboard** - Usage metrics
8. **A/B Testing** - Response optimization
