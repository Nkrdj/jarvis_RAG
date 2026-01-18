from mcp.server.fastmcp import FastMCP
import os
import logging
from simple_rag import SimpleRAG
from duckduckgo_search import DDGS
import subprocess
import shlex
import sqlite3
import json


# Initialize MCP Server
mcp = FastMCP("RAG Knowledge Base")

# Global RAG instance
rag_instance = None

def get_rag():
    """
    Lazy initialization of the RAG engine.
    """
    global rag_instance
    if rag_instance is None:
        rag_instance = SimpleRAG()
        
        # Add default knowledge
        initial_knowledge = [
             "RAG stands for Retrieval-Augmented Generation.",
             "The retrieval step finds relevant documents based on semantic similarity.",
             "Embeddings are vector representations of text where similar meanings have close vectors.",
             "Fine-tuning an LLM updates its weights, while RAG provides context without changing weights.",
             "Cosine similarity is a common metric used to measure distance between two embedding vectors.",
             "Flan-T5 is a text-to-text model capable of following instructions.",
             "To make a RAG functional, you need both a Retriever and a Generator."
        ]
        rag_instance.add_documents(initial_knowledge)
        
        
        # Note: We do NOT auto-scan docs here anymore because SimpleRAG loads from DB on init.
        # If user wants to ingest new files, they should call reload_documents() or we can check for diffs.
        # But to be safe, we can do a quick scan to see if there are *new* files not in DB?
        # For this "Simple" version, let's trust the DB + explicit reload.
        pass
        
    return rag_instance

def scan_docs(rag):
    """
    Scans the current directory for PDF and DOCX files.
    """
    count = 0
    for filename in os.listdir('.'):
        if filename.lower().endswith('.pdf'):
            rag.load_pdf(filename)
            count += 1
        elif filename.lower().endswith('.docx'):
            rag.load_docx(filename)
            count += 1
    return count

@mcp.tool()
def query_rag(query: str) -> str:
    """
    Query the RAG knowledge base.
    Args:
        query: The question to ask the AI.
    """
    rag = get_rag()
    
    # Retrieve relevant documents
    retrieved = rag.retrieve(query, top_k=3)
    
    if not retrieved:
        return "No relevant documents found in the knowledge base."
        
    # Format context
    context = " ".join([doc['document'] for doc in retrieved])
    
    # Generate answer
    answer = rag.generate_response(query, context)
    return answer

@mcp.tool()
def add_knowledge(text: str) -> str:
    """
    Add a piece of text to the knowledge base directly.
    Args:
        text: The text content to add.
    """
    rag = get_rag()
    rag.add_documents([text])
    return "Successfully added text to knowledge base."

@mcp.tool()
def reload_documents() -> str:
    """
    Rescan the current directory for PDF and DOCX files.
    Use this if you added new files to the folder.
    """
    rag = get_rag()
    count = scan_docs(rag)
    return f"Reloaded documents. Found {count} files. Total chunks: {len(rag.documents)}"

@mcp.tool()
def web_search(query: str, max_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo.
    Args:
        query: The search query.
        max_results: Max number of results to return (default 3).
    """
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."
        
        formatted = []
        for r in results:
            formatted.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}")
            
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error performing search: {str(e)}"

@mcp.tool()
def execute_command(command: str) -> str:
    """
    Execute a terminal command.
    WARNING: Use with caution.
    Args:
        command: The command to execute (e.g. 'dir', 'echo hello').
    """
    try:
        # Security check: trivial, but better than nothing
        if "rm " in command and "-rf" in command:
             return "Command blocked for safety."
             
        # Run command
        # shell=True is needed for some windows commands like 'dir' to work easily, but is improved by using powershell syntax if possible.
        # We'll use shell=True for broad compatibility as requested.
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        output = result.stdout
        if result.stderr:
            output += f"\n[Stderr]:\n{result.stderr}"
            
        return output if output.strip() else "[Command executed successfully with no output]"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@mcp.tool()
def analyze_image_file(image_path: str) -> str:
    """
    Analyze an image and return a description/caption.
    Args:
        image_path: Absolute path to the image file.
    """
    rag = get_rag()
    # Check if file exists
    if not os.path.exists(image_path):
        return f"Error: File not found at {image_path}"
        
    return rag.analyze_image(image_path)

@mcp.tool()
def query_database(sql_query: str) -> str:
    """
    Execute a read-only SQL query on the knowledge base.
    Tables: documents(id, content, source), embeddings(doc_id, embedding)
    Args:
        sql_query: The SQL query to execute (must start with SELECT).
    """
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."
        
    try:
        conn = sqlite3.connect("knowledge_base.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()
        return json.dumps(rows, default=str)
    except Exception as e:
        return f"Database Error: {str(e)}"

if __name__ == "__main__":
    # Start the MCP server
    import sys
    print("MCP Server starting... (Waiting for client connection on stdin)", file=sys.stderr)
    print("Press Ctrl+C to stop.", file=sys.stderr)
    
    # This will run over stdio by default
    mcp.run()
