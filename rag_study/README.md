# Simple RAG for Study

This project is a minimal, fully functional implementation of Retrieval-Augmented Generation (RAG).

## Components

1.  **Retriever**: Uses `sentence-transformers` (Model: `all-MiniLM-L6-v2`) to convert text into vector embeddings and finds relevant documents using Cosine Similarity.
2.  **Generator**: Uses a local LLM `google/flan-t5-base` via HuggingFace `transformers` to generate natural language answers based on the retrieved context.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script to start an interactive session:

```bash
python simple_rag.py
```

The script will:
1.  Download the models (first run only, ~1GB total).
2.  Index the internal "Knowledge Base" (a list of strings about RAG).
3.  Let you ask questions like "What is RAG?" or "How does retrieval work?".

## learning

- Look at `simple_rag.py` to see the `retrieve` vs `generate` separation.
- Try changing `top_k` in the retrieve step to feed more documents to the LLM.
- Try adding more strings to the `knowledge_base` list to teach it new things!
