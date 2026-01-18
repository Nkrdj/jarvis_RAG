from simple_rag import SimpleRAG
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest():
    print("Initializing RAG...")
    rag = SimpleRAG()
    
    print(f"Current DB documents: {len(rag.documents)}")
    
    print("Scanning current directory for new files...")
    count = 0
    for filename in os.listdir('.'):
        try:
            if filename.lower().endswith('.pdf'):
                print(f"Ingesting {filename}...")
                rag.load_pdf(filename)
                count += 1
            elif filename.lower().endswith('.docx'):
                print(f"Ingesting {filename}...")
                rag.load_docx(filename)
                count += 1
        except Exception as e:
            print(f"Failed to ingest {filename}: {e}")
            
    print(f"Ingestion complete. Added {count} files.")
    print(f"Total documents in DB: {len(rag.documents)}")

if __name__ == "__main__":
    ingest()
