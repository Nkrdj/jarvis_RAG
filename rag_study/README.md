# RAG Knowledge Base with Industrial LLMs

This project implements a Retrieval-Augmented Generation (RAG) system with **industry-standard LLM support**. It allows you to query a local knowledge base from multiple sources including PDF, DOCX files, and **YouTube videos** using professional AI models like **GPT-4o, Claude, and Gemini**!

## ✨ Features

- 📄 **Multi-Format Support**: PDF, DOCX, and YouTube video transcripts
- 🧠 **Intelligent Retrieval**: Semantic search using sentence embeddings
- 🤖 **Industrial LLMs**: OpenAI GPT-4o, Anthropic Claude, Google Gemini, or local models
- 🌐 **Web Search Fallback**: Automatically searches the web for unknown queries
- 🎬 **YouTube Integration**: Extract and index video transcripts
- 💾 **Persistent Storage**: SQLite database for knowledge persistence
- 🔌 **MCP Server**: Expose as tools for AI agents

## 🎯 Supported LLMs

- **OpenAI** (GPT-4o, GPT-4, GPT-3.5) - Recommended for best balance
- **Anthropic** (Claude 3.5 Sonnet, Claude 3 Opus) - Best quality
- **Google** (Gemini 2.0 Flash, Gemini 1.5 Pro) - FREE tier available
- **Local** (flan-t5-base) - No API key required

## Components

1.  **Retriever**: Uses `sentence-transformers` (Model: `all-MiniLM-L6-v2`) to convert text into vector embeddings.
2.  **Generator**: Supports OpenAI, Anthropic, Google Gemini, or local flan-t5-base models.
3.  **YouTube Processor**: Uses `youtube-transcript-api` to extract video transcripts.
4.  **MCP Server**: Uses `mcp` (FastMCP) to expose tools (`query_rag`, `add_knowledge`, `reload_documents`).

## 🚀 Quick Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Setup your LLM** (Interactive):
    ```bash
    python setup_llm.py
    ```
    
    Or create `.env` file manually - see **[LLM_SETUP_GUIDE.md](LLM_SETUP_GUIDE.md)**

3.  **Start using it:**
    ```bash
    python simple_rag.py
    ```


## Usage

### Method 1: Interactive RAG Shell (Standalone)
```bash
python simple_rag.py
```

Features:
- Ask questions and get AI-powered answers
- Automatically detects and processes YouTube URLs
- Web search fallback for unknown queries
- Just paste a YouTube URL and it will be indexed automatically!

### Method 2: YouTube-Focused Testing
```bash
python test_youtube.py
```

Great for testing YouTube video integration specifically.

### Method 3: Interactive Demo
```bash
python demo_youtube.py
```

Guided demonstration of YouTube integration features.

### Method 4: Running with an MCP Client (e.g., Claude Desktop)

Configure your MCP client to run the server script:

*   **Command**: `python`
*   **Arguments**: `[absolute_path_to]\\rag_mcp.py`

### Tools Available

*   **`query_rag(query)`**: Ask a question based on the documents.
*   **`add_knowledge(text)`**: Add a quick fact to the memory.
*   **`reload_documents()`**: Rescan the directory for new `.pdf` or `.docx` files.

## Adding Documents

### PDFs and DOCX Files
Simply drop `.pdf` or `.docx` files into the project root directory and call the `reload_documents` tool (or restart the server).

### YouTube Videos
**Method 1** (Interactive Shell):
```bash
python simple_rag.py
# Then paste any YouTube URL when prompted
```

**Method 2** (Programmatic):
```python
from simple_rag import SimpleRAG
rag = SimpleRAG()
rag.load_youtube_video("https://www.youtube.com/watch?v=VIDEO_ID")
```

Supported URL formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`

## 📚 Documentation

- **[YOUTUBE_SUPPORT.md](YOUTUBE_SUPPORT.md)**: Complete guide to YouTube integration
- **[test_youtube.py](test_youtube.py)**: Examples and testing scripts
- **[demo_youtube.py](demo_youtube.py)**: Interactive demonstration

## 🎯 Example Use Cases

- **Study from Lectures**: Add educational video transcripts and quiz yourself
- **Research**: Process conference talks and technical presentations
- **Learning**: Combine tutorial videos with documentation PDFs
- **Content Analysis**: Analyze multiple videos on similar topics

## 🚀 Quick Start Example

```python
from simple_rag import SimpleRAG

# Initialize
rag = SimpleRAG()

# Add a YouTube video
rag.load_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Add a PDF
rag.load_pdf("research_paper.pdf")

# Ask questions
results = rag.retrieve("What are the main concepts?", top_k=3)
context = " ".join([doc['document'] for doc in results])
answer = rag.generate_response("What are the main concepts?", context)
print(answer)
```

## 📦 Dependencies

Core:
- sentence-transformers
- transformers
- torch
- numpy
- scikit-learn

Document Processing:
- pypdf
- python-docx
- **youtube-transcript-api** (NEW!)

Additional:
- duckduckgo-search (web fallback)
- Pillow (image analysis)
- mcp (MCP server)

---

**Happy Learning! 🎓**

