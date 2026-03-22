# DocMind — RAG Chatbot

A production-grade **Retrieval Augmented Generation (RAG)** chatbot that lets you upload any document and have an intelligent conversation about its contents.

Built with **LangChain + ChromaDB + FastAPI + OpenAI**.

---

## Features

- Upload PDF, TXT, or DOCX documents
- Intelligent chunking with overlap for better context
- MMR (Maximal Marginal Relevance) retrieval for diverse results
- Conversational memory — remembers previous questions
- Source citation — shows exactly which page the answer came from
- Clean, modern dark UI built with vanilla HTML/CSS/JS
- RESTful FastAPI backend with session management

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-3.5-turbo |
| Orchestration | LangChain |
| Vector DB | ChromaDB |
| Embeddings | OpenAI text-embedding-ada-002 |
| Backend | FastAPI + Python |
| Frontend | HTML / CSS / JavaScript |

---

## Architecture

```
User uploads document
        ↓
Document Loader (PDF/TXT/DOCX)
        ↓
RecursiveCharacterTextSplitter (chunk_size=600, overlap=80)
        ↓
OpenAI Embeddings → ChromaDB Vector Store
        ↓
User asks question
        ↓
MMR Retrieval (top 4 relevant chunks)
        ↓
ConversationalRetrievalChain (with memory)
        ↓
GPT-3.5-turbo generates answer + cites sources
        ↓
Response returned to user
```

---

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/rag-chatbot
cd rag-chatbot
```

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Add your API key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 4. Start the backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Open the frontend
```bash
# Open frontend/index.html in your browser
# Or serve with Python:
cd frontend
python -m http.server 3000
# Visit http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload and process a document |
| POST | `/ask` | Ask a question about the document |
| DELETE | `/reset/{session_id}` | Clear session and memory |
| GET | `/health` | Health check |

---

## Author

**Nithish Kumar M**
B.E. Computer Science Engineering — 2026 Batch
Jai Shriram Engineering College, Tiruppur, Tamil Nadu

---

## License

MIT License — feel free to use and modify.
