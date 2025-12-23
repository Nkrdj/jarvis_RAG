import numpy as np
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader
from docx import Document

class SimpleRAG:
    def __init__(self):
        print("Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("Loading generation model (google/flan-t5-base)...")
        # pipeline downloads the model (~1GB) and handles tokenization/generation
        from transformers import pipeline
        self.generator = pipeline(
            "text2text-generation", 
            model="google/flan-t5-base", 
            device_map="auto" # uses GPU if available, else CPU
        )
        
        self.documents = []
        self.doc_embeddings = None

    def add_documents(self, docs):
        """
        Adds new documents to the existing knowledge base.
        """
        if not docs:
            return
            
        self.documents.extend(docs)
        print(f"Encoding {len(docs)} new chunks...")
        new_embeddings = self.encoder.encode(docs)
        
        if self.doc_embeddings is None:
            self.doc_embeddings = new_embeddings
        else:
            self.doc_embeddings = np.concatenate([self.doc_embeddings, new_embeddings])
            
        print(f"Total documents in knowledge base: {len(self.documents)}")

    def load_pdf(self, file_path):
        """
        Reads a PDF file and chunks the text into smaller pieces for embedding.
        Uses a sliding window approach with sentence/paragraph preservation where possible.
        """
        print(f"Processing PDF: {file_path}")
        try:
            reader = PdfReader(file_path)
            chunks = []
            current_chunk = ""
            
            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Split by newline to preserve some structure
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Add line to current chunk
                    if len(current_chunk) + len(line) < 500:
                        current_chunk += line + " "
                    else:
                        # Chunk is full, save it
                        chunks.append(current_chunk.strip())
                        # Start new chunk with overlap (last 50 chars of previous for context flow)
                        overlap = current_chunk[-50:] if len(current_chunk) > 50 else ""
                        current_chunk = overlap + line + " "

            if current_chunk:
                chunks.append(current_chunk.strip())
            
            print(f"Extracted {len(chunks)} chunks from {file_path}")
            self.add_documents(chunks)
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")

    def load_docx(self, file_path):
        """
        Reads a DOCX file and chunks the text.
        """
        print(f"Processing DOCX: {file_path}")
        try:
            doc = Document(file_path)
            chunks = []
            current_chunk = ""
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                    
                if len(current_chunk) + len(text) < 500:
                    current_chunk += text + " "
                else:
                    chunks.append(current_chunk.strip())
                    overlap = current_chunk[-50:] if len(current_chunk) > 50 else ""
                    current_chunk = overlap + text + " "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
                
            print(f"Extracted {len(chunks)} chunks from {file_path}")
            self.add_documents(chunks)
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")

    def retrieve(self, query, top_k=3):
        if self.doc_embeddings is None:
            return []
            
        query_embedding = self.encoder.encode([query])
        similarities = cosine_similarity(query_embedding, self.doc_embeddings)[0]
        
        # Get top indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                "score": similarities[idx],
                "document": self.documents[idx]
            })
        return results

    def generate_response(self, query, context):
        print("Generating response with LLM...")
        
        prompt = f"""Answer the question based strictly on the context below. If the answer is not in the context, say "I cannot answer this based on the provided documents."

Context:
{context}

Question: {query}
Answer:"""
        
        # Increased token limit for more detailed answers
        result = self.generator(prompt, max_new_tokens=200, do_sample=False)
        return result[0]['generated_text']

def main():
    rag = SimpleRAG()

    # 1. Add default knowledge
    initial_knowledge = [
        "RAG stands for Retrieval-Augmented Generation.",
        "The retrieval step finds relevant documents based on semantic similarity.",
        "Embeddings are vector representations of text where similar meanings have close vectors.",
        "Fine-tuning an LLM updates its weights, while RAG provides context without changing weights.",
        "Cosine similarity is a common metric used to measure distance between two embedding vectors.",
        "Flan-T5 is a text-to-text model capable of following instructions.",
        "To make a RAG functional, you need both a Retriever and a Generator."
    ]
    rag.add_documents(initial_knowledge)

    # 2. Check for PDF and DOCX in current directory
    print("\nScanning for documents in current directory...")
    found_docs = False
    for filename in os.listdir('.'):
        if filename.lower().endswith('.pdf'):
            rag.load_pdf(filename)
            found_docs = True
        elif filename.lower().endswith('.docx'):
            rag.load_docx(filename)
            found_docs = True
    
    if not found_docs:
        print("No PDF or DOCX files found. Drop files in this folder to index them!")

    while True:
        print("\n" + "="*50)
        user_query = input("Enter your question (or 'quit' to exit): ")
        if user_query.lower() in ['quit', 'exit']:
            break

        print(f"Searching for: {user_query}")
        
        # Retrieve
        retrieved_docs = rag.retrieve(user_query, top_k=3)
        
        context = ""
        print("\n[Retrieved Context]:")
        for doc in retrieved_docs:
            snippet = doc['document'].replace('\n', ' ')[:100] + "..."
            print(f"- {snippet} (Score: {doc['score']:.4f})")
            context += doc['document'] + " "

        # Generate
        print("\n[LLM Answer]:")
        answer = rag.generate_response(user_query, context)
        print(answer)

if __name__ == "__main__":
    main()
