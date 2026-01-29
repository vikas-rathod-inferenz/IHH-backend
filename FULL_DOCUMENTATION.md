# 🏥 Medical Assistant Backend - Complete Project Documentation

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement & Solution](#2-problem-statement--solution)
3. [System Architecture](#3-system-architecture)
4. [Complete Workflow Flow](#4-complete-workflow-flow)
5. [File Structure & Purpose](#5-file-structure--purpose)
6. [Component Deep Dive](#6-component-deep-dive)
7. [Technical Stack](#7-technical-stack)
8. [API Documentation](#8-api-documentation)
9. [Configuration Guide](#9-configuration-guide)
10. [Functionality Details](#10-functionality-details)
11. [Scope & Features](#11-scope--features)
12. [Future Scope](#12-future-scope)
13. [Deployment Guide](#13-deployment-guide)

---

## 1. Project Overview

### 1.1 What is Medical Assistant Backend?

The **Medical Assistant Backend** is an AI-powered medical chatbot system built using modern AI/ML technologies. It serves as the backend infrastructure for a medical question-answering platform that can:

- Answer medical and health-related questions accurately
- Retrieve information from a medical knowledge base (RAG)
- Search the web for latest medical research
- Validate input/output for safety and appropriateness
- Provide confidence-scored responses with source citations
- Support human-in-the-loop for expert validation

### 1.2 Key Technologies

| Technology | Purpose |
|------------|---------|
| **LangGraph** | Multi-agent orchestration and workflow management |
| **FastAPI** | High-performance REST API framework |
| **ChromaDB** | Vector database for semantic search |
| **Azure OpenAI** | LLM (GPT-4o) and embeddings |
| **Tavily API** | Real-time web search for medical research |
| **HuggingFace Transformers** | Cross-encoder for document reranking |

### 1.3 Project Statistics

| Metric | Value |
|--------|-------|
| Total Files | 30+ |
| Core Modules | 4 (agents, core, utils, app) |
| Agent Types | 4 (RAG, Web Search, Guardrails, Image Analysis*) |
| API Endpoints | 8 |
| Documentation Pages | 5 |

*Image Analysis is a placeholder for future implementation

---

## 2. Problem Statement & Solution

### 2.1 Problems This Project Solves

#### Problem 1: Information Overload
**Challenge:** Users struggle to find accurate, reliable medical information online due to:
- Overwhelming amount of health information
- Contradictory advice from different sources
- Difficulty distinguishing credible sources

**Solution:** The system uses RAG (Retrieval-Augmented Generation) with a curated medical knowledge base, ensuring answers come from verified medical documents.

#### Problem 2: Lack of Context-Aware Responses
**Challenge:** Traditional search engines return generic results without understanding:
- Medical terminology
- User's specific context
- Related symptoms and conditions

**Solution:** Query expansion with medical terminology and semantic search provides context-aware, comprehensive answers.

#### Problem 3: Outdated Medical Information
**Challenge:** Medical knowledge evolves rapidly:
- New research is published daily
- Treatment guidelines change
- Static knowledge bases become outdated

**Solution:** Web search integration fetches the latest research from trusted sources like PubMed, NIH, Mayo Clinic, etc.

#### Problem 4: Safety & Misinformation
**Challenge:** Medical chatbots can potentially:
- Provide harmful advice
- Miss emergency situations
- Give inaccurate diagnoses

**Solution:** Multi-layer guardrails system validates both input and output:
- Emergency detection
- Inappropriate content filtering
- Medical disclaimer enforcement
- Human review for uncertain responses

#### Problem 5: Lack of Transparency
**Challenge:** Users don't know:
- Where the information comes from
- How confident the system is
- Whether to trust the response

**Solution:** Confidence scoring and source citation provide full transparency:
- Every response includes sources
- Confidence scores guide trust levels
- Low confidence triggers human review

### 2.2 Target Users

1. **Patients** - Seeking health information
2. **Caregivers** - Managing family health questions
3. **Healthcare Administrators** - Building patient support systems
4. **Medical Researchers** - Quick literature synthesis
5. **Healthcare Startups** - Building medical AI applications

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT APPLICATIONS                         │
│          (Web Frontend, Mobile Apps, API Integrations)           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                          │
│                     (app.py - Port 8000)                         │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │   /chat     │  │  /upload    │  │  /health    │            │
│   │   endpoint  │  │  endpoint   │  │  endpoint   │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
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
│  │  Agent       │  │  Web Search  │  │  Review      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                ▼                ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   ChromaDB       │  │  Azure OpenAI    │  │  Tavily Search   │
│  Vector Store    │  │  - LLM (GPT-4o)  │  │  Web API         │
│  - Embeddings    │  │  - Embeddings    │  │  - PubMed        │
│  - Similarity    │  │  - Generation    │  │  - NIH, Mayo     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### 3.2 Multi-Agent Architecture

The system uses a **multi-agent architecture** where specialized agents handle different aspects:

```
                    ┌─────────────────────┐
                    │    Orchestrator     │
                    │   (LangGraph)       │
                    └─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Guardrails   │    │  RAG Agent    │    │  Web Search   │
│    Agent      │    │               │    │    Agent      │
│               │    │ ┌───────────┐ │    │               │
│ • Input Check │    │ │Vector     │ │    │ • Tavily API  │
│ • Output Check│    │ │Store      │ │    │ • Source      │
│ • Emergency   │    │ │Query Exp. │ │    │   Synthesis   │
│   Detection   │    │ │Reranker   │ │    │ • Citation    │
└───────────────┘    │ └───────────┘ │    └───────────────┘
                     └───────────────┘
                              │
                     ┌───────────────┐
                     │ Image Agent   │
                     │ (Future)      │
                     └───────────────┘
```

---

## 4. Complete Workflow Flow

### 4.1 Main Processing Flow

```
User Question
      │
      ▼
┌─────────────────┐
│ 1. INPUT        │ ──▶ Guardrails check safety & relevance
│    VALIDATION   │     • Is it medical-related?
└────────┬────────┘     • Is it an emergency?
         │              • Is it appropriate?
         │
    ┌────┴────┐
    │ Valid?  │
    └────┬────┘
    NO   │   YES
    │    │    │
    ▼    │    ▼
 Return  │  ┌─────────────────┐
 Error   │  │ 2. AGENT        │ ──▶ Decide which agent to use
         │  │    DECISION     │     • Default: RAG first
         │  └────────┬────────┘     • Route based on query type
         │           │
         │           ▼
         │  ┌─────────────────┐
         │  │ 3. RAG AGENT    │ ──▶ Retrieve from knowledge base
         │  │                 │     • Query Expansion
         │  │                 │     • Vector Search
         │  │                 │     • Reranking
         │  │                 │     • Generate Response
         │  └────────┬────────┘
         │           │
         │    ┌──────┴──────┐
         │    │ Confidence  │
         │    │   ≥ 0.7?    │
         │    └──────┬──────┘
         │      YES  │   NO
         │      │    │    │
         │      │    │    ▼
         │      │    │  ┌─────────────────┐
         │      │    │  │ 4. WEB SEARCH   │ ──▶ Search latest research
         │      │    │  │    AGENT        │     • Tavily API
         │      │    │  └────────┬────────┘     • Medical sources
         │      │    │           │
         │      │    │           ▼
         │      │    │  ┌─────────────────┐
         │      │    │  │ 5. COMBINE      │ ──▶ Merge RAG + Web results
         │      │    │  │    RESULTS      │
         │      │    │  └────────┬────────┘
         │      │    │           │
         │      ▼    ▼           ▼
         │  ┌─────────────────────────┐
         │  │ 6. OUTPUT VALIDATION    │ ──▶ Guardrails check response
         │  │                         │     • Medical accuracy
         │  └────────────┬────────────┘     • Safety disclaimers
         │               │                  • Harmful content
         │        ┌──────┴──────┐
         │        │ Confidence  │
         │        │   ≥ 0.7?    │
         │        └──────┬──────┘
         │          YES  │   NO
         │          │    │    │
         │          │    │    ▼
         │          │    │  ┌─────────────────┐
         │          │    │  │ 7. HUMAN        │ ──▶ Flag for expert review
         │          │    │  │    REVIEW       │     • Add disclaimer
         │          │    │  └────────┬────────┘
         │          │    │           │
         │          ▼    ▼           ▼
         │  ┌─────────────────────────┐
         │  │ 8. FINALIZE             │ ──▶ Prepare final response
         │  │                         │
         │  └────────────┬────────────┘
         │               │
         ▼               ▼
┌─────────────────────────────────┐
│         FINAL RESPONSE          │
│ • Answer text                   │
│ • Sources with citations        │
│ • Confidence score              │
│ • Agent path (transparency)     │
│ • Processing time               │
│ • Warnings (if any)             │
└─────────────────────────────────┘
```

### 4.2 RAG Pipeline Flow

```
User Query: "What are symptoms of diabetes?"
                │
                ▼
┌──────────────────────────────────────────────────────┐
│  STEP 1: QUERY EXPANSION                             │
│                                                      │
│  Input:  "symptoms of diabetes"                      │
│  Output: "diabetes, type 1 diabetes, type 2          │
│           diabetes, hyperglycemia, polyuria,         │
│           polydipsia, diabetic symptoms, glycemic"   │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│  STEP 2: VECTOR SEARCH (ChromaDB)                    │
│                                                      │
│  • Convert expanded query to embedding vector        │
│  • Similarity search in vector store                 │
│  • Retrieve top K documents (default: 15)            │
│  • Returns documents with relevance scores           │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│  STEP 3: RERANKING (Cross-Encoder)                   │
│                                                      │
│  • Use HuggingFace cross-encoder model               │
│  • Score each document against original query        │
│  • Sort by relevance score                           │
│  • Keep top 3 most relevant documents                │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│  STEP 4: CONFIDENCE CALCULATION                      │
│                                                      │
│  • Average relevance scores                          │
│  • Apply document count factor                       │
│  • Normalize to 0-1 range                            │
│  • Example: confidence = 0.82                        │
└──────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────┐
│  STEP 5: RESPONSE GENERATION                         │
│                                                      │
│  • Combine retrieved documents as context            │
│  • Send to Azure OpenAI GPT-4o                       │
│  • Generate comprehensive medical response           │
│  • Include medical disclaimers                       │
└──────────────────────────────────────────────────────┘
```

### 4.3 State Machine Flow (LangGraph)

```
                        START
                          │
                          ▼
                ┌─────────────────┐
                │ input_validation│◀─────────────────────┐
                └────────┬────────┘                      │
                         │                               │
           ┌─────────────┼─────────────┐                │
           │             │             │                │
      (invalid)      (valid)      (emergency)           │
           │             │             │                │
           ▼             ▼             ▼                │
      ┌────────┐  ┌─────────────┐  ┌────────┐         │
      │ END    │  │agent_decision│  │ END    │         │
      │(error) │  └──────┬──────┘  │(refer) │         │
      └────────┘         │          └────────┘         │
                         │                              │
           ┌─────────────┼─────────────┐               │
           │             │             │               │
        (rag)         (both)     (web_search)          │
           │             │             │               │
           ▼             ▼             ▼               │
      ┌─────────┐   ┌─────────┐  ┌─────────────┐      │
      │rag_agent│   │rag_agent│  │web_search   │      │
      └────┬────┘   └────┬────┘  │agent        │      │
           │             │        └──────┬──────┘      │
           │             │               │             │
    ┌──────┴──────┐      │               │             │
    │ confidence  │      │               │             │
    │   ≥ 0.7?    │      │               │             │
    └──────┬──────┘      │               │             │
      YES  │   NO        │               │             │
      │    │    │        │               │             │
      │    │    ▼        │               │             │
      │    │  ┌──────────┴───────┐       │             │
      │    │  │ web_search_agent │       │             │
      │    │  └────────┬─────────┘       │             │
      │    │           │                 │             │
      │    │           ▼                 │             │
      │    │    ┌──────────────┐         │             │
      │    │    │combine_results│◀───────┘             │
      │    │    └──────┬───────┘                       │
      │    │           │                               │
      ▼    ▼           ▼                               │
      ┌────────────────────┐                           │
      │ output_validation  │                           │
      └─────────┬──────────┘                           │
                │                                      │
     ┌──────────┼──────────┐                          │
     │          │          │                          │
 (approved) (human_review) (retry)                    │
     │          │          │                          │
     │          ▼          └──────────────────────────┘
     │    ┌────────────┐
     │    │human_review│
     │    └─────┬──────┘
     │          │
     ▼          ▼
    ┌────────────┐
    │  finalize  │
    └─────┬──────┘
          │
          ▼
         END
```

---

## 5. File Structure & Purpose

### 5.1 Complete File Map

```
medical_assistant_backend/
│
├── 📄 app.py                    # Main FastAPI application entry point
├── 📄 config.py                 # Configuration management (env variables)
├── 📄 ingest_documents.py       # Document ingestion script for knowledge base
├── 📄 test_api.py               # API testing script
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env                      # Environment variables (API keys)
├── 📄 .env.example              # Environment template
├── 📄 Dockerfile                # Docker container configuration
├── 📄 docker-compose.yml        # Docker orchestration
├── 📄 .gitignore                # Git ignore patterns
│
├── 📁 agents/                   # Multi-agent system
│   ├── 📄 __init__.py
│   │
│   ├── 📁 guardrails/           # Safety guardrails agent
│   │   ├── 📄 __init__.py
│   │   └── 📄 guardrails.py     # Input/output validation
│   │
│   ├── 📁 rag_agent/            # RAG retrieval agent
│   │   ├── 📄 __init__.py
│   │   ├── 📄 rag_agent.py      # Main RAG orchestration
│   │   ├── 📄 vector_store.py   # ChromaDB integration
│   │   ├── 📄 query_expander.py # Medical query expansion
│   │   └── 📄 reranker.py       # Cross-encoder reranking
│   │
│   ├── 📁 web_search_agent/     # Web search agent
│   │   ├── 📄 __init__.py
│   │   ├── 📄 web_search_agent.py # Search orchestration
│   │   └── 📄 tavily_search.py  # Tavily API wrapper
│   │
│   └── 📁 image_analysis_agent/ # Image analysis (placeholder)
│       └── 📄 __init__.py
│
├── 📁 core/                     # Core orchestration
│   ├── 📄 __init__.py
│   ├── 📄 orchestrator.py       # LangGraph workflow engine
│   └── 📄 state.py              # Graph state definition
│
├── 📁 utils/                    # Utility modules
│   ├── 📄 __init__.py
│   ├── 📄 logger.py             # Logging configuration
│   └── 📄 models.py             # Pydantic data models
│
├── 📁 data/                     # Data storage
│   └── 📁 chroma_db/            # ChromaDB persistence
│       └── chroma.sqlite3
│
├── 📁 uploads/                  # Document uploads
│
├── 📁 logs/                     # Application logs
│
└── 📁 __pycache__/              # Python bytecode cache
```

### 5.2 File Purpose Details

| File | Purpose | Key Functions |
|------|---------|---------------|
| **app.py** | API entry point | `chat()`, `health_check()`, `upload_document()` |
| **config.py** | Settings management | Load env vars, validate settings |
| **orchestrator.py** | Workflow engine | `process_query()`, `_build_graph()` |
| **state.py** | State definition | `GraphState` TypedDict |
| **guardrails.py** | Safety checks | `validate_input()`, `validate_output()` |
| **rag_agent.py** | RAG pipeline | `query()`, `retrieve_documents()`, `generate_response()` |
| **vector_store.py** | Vector DB | `similarity_search()`, `add_documents()` |
| **query_expander.py** | Query enhancement | `expand_query()`, `create_expanded_query()` |
| **reranker.py** | Document ranking | `rerank()` |
| **web_search_agent.py** | Web search | `query()`, `synthesize_results()` |
| **tavily_search.py** | Tavily API | `search()`, `medical_search()` |
| **models.py** | Data schemas | `ChatRequest`, `ChatResponse`, `Source` |
| **logger.py** | Logging setup | `setup_logging()`, `get_logger()` |
| **ingest_documents.py** | Data ingestion | `ingest_documents_from_directory()` |

---

## 6. Component Deep Dive

### 6.1 FastAPI Application (app.py)

**Purpose:** Main entry point providing REST API endpoints

**Key Features:**
- Async request handling
- CORS middleware for cross-origin requests
- Global exception handling
- Health monitoring
- Document upload support

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root - API info |
| `/chat` | POST | Main chat interface |
| `/health` | GET | Health check |
| `/documents/upload` | POST | Upload documents |
| `/documents/collection-info` | GET | Vector store info |
| `/docs` | GET | Swagger documentation |
| `/redoc` | GET | ReDoc documentation |

### 6.2 LangGraph Orchestrator (orchestrator.py)

**Purpose:** Manages the multi-agent workflow using state machines

**Workflow Nodes:**
1. `input_validation` - Guardrails input check
2. `agent_decision` - Route to appropriate agent
3. `rag_agent` - Knowledge base retrieval
4. `web_search_agent` - Web research
5. `combine_results` - Merge multi-source results
6. `output_validation` - Safety check on response
7. `human_review` - Expert validation (low confidence)
8. `finalize` - Prepare final response

**Routing Functions:**
- `route_after_input_validation()` - Valid → proceed, Invalid → end
- `route_to_agents()` - RAG, Web Search, or Both
- `route_after_rag()` - Sufficient confidence → output, Low → web search
- `route_after_output_validation()` - Approved → finalize, Low → human review

### 6.3 RAG Agent (rag_agent/)

**Purpose:** Retrieval-Augmented Generation for knowledge base queries

**Components:**

#### Vector Store (vector_store.py)
- ChromaDB integration
- Azure OpenAI embeddings
- Similarity search
- MMR (Maximum Marginal Relevance) search
- Collection management

#### Query Expander (query_expander.py)
- Expands queries with medical synonyms
- Uses LLM for intelligent expansion
- Improves retrieval coverage

**Example:**
```
Input: "headache treatment"
Output: "headache, migraine, cephalalgia, analgesics, 
        pain relief, NSAIDs, tension headache"
```

#### Reranker (reranker.py)
- Uses HuggingFace cross-encoder
- Model: `cross-encoder/ms-marco-TinyBERT-L-6`
- Reranks documents by relevance
- GPU acceleration when available

### 6.4 Web Search Agent (web_search_agent/)

**Purpose:** Real-time web search for latest medical research

**Components:**

#### Tavily Search (tavily_search.py)
- Tavily API integration
- Medical domain filtering
- Trusted sources focus:
  - PubMed
  - NIH
  - Mayo Clinic
  - WHO
  - CDC
  - The Lancet
  - NEJM

#### Search Agent (web_search_agent.py)
- Search execution
- Result synthesis with LLM
- Source citation management

### 6.5 Guardrails Agent (guardrails.py)

**Purpose:** Safety validation for inputs and outputs

**Input Validation Checks:**
- Medical relevance
- Emergency detection
- Inappropriate content filtering
- Scope verification

**Output Validation Checks:**
- Medical accuracy
- Disclaimer verification
- Harmful content detection
- Bias detection

**Categories:**
- `medical_query` - Standard medical question
- `emergency` - Requires immediate care
- `off_topic` - Not medical related
- `inappropriate` - Harmful/illegal content

### 6.6 State Management (state.py)

**Purpose:** Defines the graph state structure

**State Properties:**

```python
class GraphState(TypedDict):
    # Input
    question: str
    user_id: Optional[str]
    session_id: Optional[str]
    
    # Processing flags
    input_validated: bool
    is_medical: bool
    is_emergency: bool
    category: str
    
    # Agent routing
    current_agent: Optional[str]
    requires_rag: bool
    requires_web_search: bool
    requires_human_review: bool
    
    # RAG results
    rag_documents: List[Document]
    rag_response: Optional[str]
    rag_confidence: float
    rag_sources: List[Dict]
    
    # Web search results
    web_search_response: Optional[str]
    web_search_sources: List[Dict]
    web_search_confidence: float
    
    # Final output
    final_response: str
    final_sources: List[Dict]
    final_confidence: float
    output_validated: bool
    
    # Human-in-the-loop
    human_feedback: Optional[str]
    human_approved: Optional[bool]
    
    # Metadata
    error: Optional[str]
    warnings: List[str]
    processing_time: float
    agent_path: List[str]
```

---

## 7. Technical Stack

### 7.1 Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104+ | REST API |
| **Orchestration** | LangGraph | 0.0.45+ | Agent workflow |
| **LLM** | Azure OpenAI | GPT-4o | Response generation |
| **Vector DB** | ChromaDB | 0.4+ | Document storage |
| **Embeddings** | Azure OpenAI | text-embedding-ada-002 | Semantic search |
| **Reranking** | HuggingFace | cross-encoder | Document ranking |
| **Web Search** | Tavily | - | Real-time search |
| **Validation** | Pydantic | 2.0+ | Data validation |

### 7.2 Python Dependencies

```
# Core
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0

# LangChain & LangGraph
langchain>=0.1.0
langchain-core>=0.1.0
langchain-openai>=0.0.3
langchain-community>=0.0.10
langgraph>=0.0.45

# Vector Store
chromadb>=0.4.18

# Web Search
tavily-python>=0.3.0

# ML/Reranking
torch>=2.1.0
transformers>=4.35.0
sentence-transformers>=2.2.2

# Document Processing
python-multipart>=0.0.6
pypdf>=3.17.0
```

### 7.3 External APIs Required

| API | Purpose | Required |
|-----|---------|----------|
| Azure OpenAI | LLM & Embeddings | ✅ Yes |
| Tavily | Web Search | ✅ Yes |
| HuggingFace | Model Access | ✅ Yes |
| LangSmith | Tracing (Optional) | ❌ Optional |

---

## 8. API Documentation

### 8.1 Chat Endpoint

**POST `/chat`**

Request:
```json
{
  "question": "What are the symptoms of diabetes?",
  "user_id": "user123",
  "session_id": "session456",
  "use_expansion": true,
  "use_reranking": true
}
```

Response:
```json
{
  "response": "Diabetes symptoms include...",
  "sources": [
    {
      "index": 1,
      "title": "Diabetes Overview",
      "content": "Document excerpt...",
      "metadata": {"source": "medical_doc.pdf"}
    }
  ],
  "confidence": 0.85,
  "category": "medical_query",
  "agent_path": ["input_validation", "agent_decision", "rag_agent", "output_validation", "finalize"],
  "processing_time": 2.45,
  "warnings": [],
  "error": null
}
```

### 8.2 Document Upload

**POST `/documents/upload`**

Request: `multipart/form-data` with file

Response:
```json
{
  "success": true,
  "message": "Document processed successfully",
  "filename": "medical_guide.pdf",
  "chunks_created": 15,
  "document_ids": ["id1", "id2", "..."]
}
```

### 8.3 Health Check

**GET `/health`**

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "api": "operational",
    "vector_store": "operational",
    "document_count": "150"
  }
}
```

### 8.4 Collection Info

**GET `/documents/collection-info`**

Response:
```json
{
  "collection_name": "medical_documents",
  "document_count": 150,
  "persist_directory": "./data/chroma_db"
}
```

---

## 9. Configuration Guide

### 9.1 Environment Variables

Create `.env` file from `.env.example`:

```env
# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Azure OpenAI (LLM)
OPENAI_API_KEY=your_azure_openai_key
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
OPENAI_API_VERSION=2024-08-01-preview
MODEL_NAME=gpt-4o
DEPLOYMENT_NAME=your_deployment_name

# Azure OpenAI (Embeddings)
EMBEDDING_API_KEY=your_embedding_key
EMBEDDING_AZURE_ENDPOINT=https://your-embedding-resource.openai.azure.com/
EMBEDDING_MODEL_NAME=text-embedding-ada-002
EMBEDDING_API_VERSION=2024-08-01-preview

# Web Search
TAVILY_API_KEY=your_tavily_api_key

# HuggingFace
HUGGINGFACE_TOKEN=your_hf_token

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
RERANK_TOP_K=3
CONFIDENCE_THRESHOLD=0.7

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
CHROMA_COLLECTION_NAME=medical_documents

# File Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,txt,docx

# LangSmith (Optional)
LANGCHAIN_TRACING_V2=false
LANGSMITH_API_KEY=your_langsmith_key
```

### 9.2 Key Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `CONFIDENCE_THRESHOLD` | 0.7 | Min confidence before web search |
| `TOP_K_RETRIEVAL` | 5 | Documents to retrieve initially |
| `RERANK_TOP_K` | 3 | Documents after reranking |
| `CHUNK_SIZE` | 1000 | Document chunk size |
| `CHUNK_OVERLAP` | 200 | Overlap between chunks |
| `MAX_TOKENS` | 2000 | Max LLM response tokens |
| `TEMPERATURE` | 0.3 | LLM creativity (0=deterministic) |

---

## 10. Functionality Details

### 10.1 Query Processing Pipeline

1. **User submits question** via `/chat` endpoint
2. **Input validation** checks safety and relevance
3. **Agent decision** routes to appropriate agent
4. **RAG retrieval** fetches relevant documents
5. **Query expansion** enriches search terms
6. **Vector search** finds semantically similar documents
7. **Reranking** orders by relevance
8. **Confidence check** determines if web search needed
9. **Web search** (if confidence < 0.7) fetches latest research
10. **Result combination** merges all sources
11. **Output validation** ensures safety
12. **Human review** (if confidence < 0.7) flags for expert
13. **Response returned** with sources and metadata

### 10.2 Safety Features

| Feature | Implementation |
|---------|---------------|
| Emergency Detection | LLM classifier identifies crisis situations |
| Content Filtering | Blocks inappropriate/harmful requests |
| Medical Disclaimers | Automatically added to responses |
| Confidence Scoring | Quantifies answer reliability |
| Human Review Flag | Low-confidence responses marked |
| Source Citation | Full transparency on information sources |

### 10.3 Intelligent Routing

```python
# Routing logic in orchestrator
def route_after_rag(state):
    confidence = state["rag_confidence"]
    if confidence >= 0.7:
        return "sufficient"  # Use RAG response
    else:
        return "need_web_search"  # Augment with web
```

---

## 11. Scope & Features

### 11.1 Current Features

| Feature | Status | Description |
|---------|--------|-------------|
| Multi-Agent Architecture | ✅ Complete | LangGraph orchestration |
| RAG System | ✅ Complete | ChromaDB + Azure OpenAI |
| Query Expansion | ✅ Complete | Medical terminology |
| Document Reranking | ✅ Complete | Cross-encoder model |
| Web Search | ✅ Complete | Tavily integration |
| Input Guardrails | ✅ Complete | Safety validation |
| Output Guardrails | ✅ Complete | Response validation |
| Confidence Scoring | ✅ Complete | Quality assessment |
| Human-in-the-Loop | ✅ Complete | Expert review flag |
| Document Upload | ✅ Complete | PDF, TXT, DOCX |
| REST API | ✅ Complete | FastAPI endpoints |
| Docker Support | ✅ Complete | Containerization |
| Logging | ✅ Complete | Rotating file logs |

### 11.2 Project Scope

**In Scope:**
- Medical question answering
- Health information retrieval
- Latest research synthesis
- Safety guardrails
- Source citation
- Confidence assessment

**Out of Scope:**
- Medical diagnosis
- Treatment prescriptions
- Emergency medical care
- Personal health records
- Appointment scheduling
- Telemedicine features

### 11.3 Limitations

1. **Not a replacement for medical professionals**
2. **Cannot provide emergency medical advice**
3. **Knowledge limited to ingested documents + web search**
4. **Requires internet for web search functionality**
5. **API costs for Azure OpenAI and Tavily**

---

## 12. Future Scope

### 12.1 Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **Image Analysis Agent** | High | Brain tumor, X-ray, skin lesion analysis |
| **PubMed Integration** | High | Direct PubMed API access |
| **Voice Interface** | Medium | Eleven Labs TTS integration |
| **Conversation Memory** | Medium | Multi-turn conversations |
| **User Profiles** | Medium | Personalized responses |
| **Admin Dashboard** | Low | Analytics and monitoring |

### 12.2 Image Analysis Capabilities (Planned)

```
┌─────────────────────────────────────────────┐
│           IMAGE ANALYSIS AGENT              │
│                                             │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Brain Tumor    │  │  Chest X-Ray    │  │
│  │  Detection      │  │  Analysis       │  │
│  └─────────────────┘  └─────────────────┘  │
│                                             │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Skin Lesion    │  │  Retinal Scan   │  │
│  │  Segmentation   │  │  Analysis       │  │
│  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────┘
```

### 12.3 Technical Improvements

1. **Caching Layer** - Redis for response caching
2. **Rate Limiting** - API abuse prevention
3. **Load Balancing** - Multiple instance support
4. **A/B Testing** - Response quality optimization
5. **Feedback Loop** - User rating integration
6. **Fine-tuned Models** - Medical domain adaptation

### 12.4 Integration Possibilities

- **Healthcare EHR Systems** - FHIR/HL7 integration
- **Telehealth Platforms** - Pre-consultation assistant
- **Patient Portals** - After-visit summaries
- **Clinical Decision Support** - Physician assistant
- **Medical Education** - Student learning tool

---

## 13. Deployment Guide

### 13.1 Local Development

```bash
# 1. Clone repository
cd d:\IHH\medical_assistant_backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your API keys

# 5. Ingest sample data (optional)
python ingest_documents.py

# 6. Run application
python app.py
# Or: uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 13.2 Docker Deployment

```bash
# Build image
docker build -t medical-assistant-backend .

# Run container
docker run -p 8000:8000 --env-file .env medical-assistant-backend

# Or use docker-compose
docker-compose up -d
```

### 13.3 Production Considerations

1. **Environment Variables** - Use secure secret management
2. **CORS Configuration** - Restrict to specific domains
3. **Rate Limiting** - Implement API throttling
4. **HTTPS** - Enable SSL/TLS
5. **Monitoring** - Set up health checks and alerts
6. **Logging** - Centralized log aggregation
7. **Backup** - Regular ChromaDB backups
8. **Scaling** - Horizontal scaling with load balancer

---

## 📞 Support & Resources

- **API Documentation:** http://localhost:8000/docs
- **Logs Directory:** `./logs/`
- **Configuration:** `config.py`
- **Health Check:** http://localhost:8000/health

---

## 📝 Document Information

| Property | Value |
|----------|-------|
| **Document Version** | 1.0.0 |
| **Created** | January 29, 2026 |
| **Project Status** | ✅ Complete |
| **Author** | Medical Assistant Development Team |

---

*This document provides a complete technical and functional overview of the Medical Assistant Backend project. For specific implementation details, refer to the source code and inline documentation.*
