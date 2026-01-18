import numpy as np
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
from db import KnowledgeDB
import re
import logging
import sys
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SimpleRAG:
    def __init__(self):
        logger.info("Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load environment variables
        load_dotenv()
        
        # Configure LLM provider
        self.llm_provider = os.getenv('LLM_PROVIDER', 'local').lower()
        logger.info(f"LLM Provider: {self.llm_provider}")
        
        # Initialize LLM based on provider
        if self.llm_provider == 'openai':
            self._init_openai()
        elif self.llm_provider == 'anthropic':
            self._init_anthropic()
        elif self.llm_provider == 'google':
            self._init_google()
        elif self.llm_provider == 'local':
            self._init_local_model()
        else:
            logger.warning(f"Unknown provider '{self.llm_provider}', falling back to local")
            self._init_local_model()
        
        self.db = KnowledgeDB()
        self.documents = []
        self.doc_embeddings = None
        
        # Load existing knowledge from DB
        self.load_from_db()
    
    def _init_openai(self):
        """Initialize OpenAI LLM"""
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key or api_key == 'your-openai-api-key-here':
                logger.error("OpenAI API key not set!")
                self._init_local_model()
                return
            
            self.client = OpenAI(api_key=api_key)
            self.model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            logger.info(f"✅ OpenAI initialized: {self.model_name}")
        except Exception as e:
            logger.error(f"OpenAI init failed: {e}")
            self._init_local_model()
    
    def _init_anthropic(self):
        """Initialize Anthropic Claude LLM"""
        try:
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key or api_key == 'your-anthropic-api-key-here':
                logger.error("Anthropic API key not set!")
                self._init_local_model()
                return
            
            self.client = Anthropic(api_key=api_key)
            self.model_name = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
            logger.info(f"✅ Anthropic initialized: {self.model_name}")
        except Exception as e:
            logger.error(f"Anthropic init failed: {e}")
            self._init_local_model()
    
    def _init_google(self):
        """Initialize Google Gemini LLM"""
        try:
            import google.generativeai as genai
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key or api_key == 'your-google-api-key-here':
                logger.error("Google API key not set!")
                self._init_local_model()
                return
            
            genai.configure(api_key=api_key)
            self.model_name = os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash-exp')
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"✅ Google Gemini initialized: {self.model_name}")
        except Exception as e:
            logger.error(f"Google init failed: {e}")
            self._init_local_model()
    
    def _init_local_model(self):
        """Initialize local flan-t5-base model"""
        logger.info("Loading local model (flan-t5-base)...")
        from transformers import pipeline
        self.generator = pipeline(
            "text2text-generation", 
            model="google/flan-t5-base", 
            device_map="auto"
        )
        self.llm_provider = 'local'
        logger.info("✅ Local model loaded")

    def load_from_db(self):
        logger.info("Loading knowledge from database...")
        records = self.db.get_all_documents()
        if records:
            self.documents = [r['content'] for r in records]
            embeddings = [r['embedding'] for r in records]
            self.doc_embeddings = np.array(embeddings)
            logger.info(f"Loaded {len(records)} documents from DB")
        else:
            logger.info("Database is empty")

    def add_documents(self, docs, source="unknown"):
        """Add new documents to the knowledge base"""
        if not docs:
            return
            
        self.documents.extend(docs)
        logger.info(f"Encoding {len(docs)} new chunks...")
        new_embeddings = self.encoder.encode(docs)
        
        # Save to DB
        for doc, emb in zip(docs, new_embeddings):
            self.db.add_document(doc, source, emb.tolist())
        
        # Update memory
        if self.doc_embeddings is None:
            self.doc_embeddings = new_embeddings
        else:
            self.doc_embeddings = np.concatenate([self.doc_embeddings, new_embeddings])
            
        logger.info(f"Total documents: {len(self.documents)}")

    def load_docx(self, file_path):
        """Load and process DOCX file"""
        logger.info(f"Processing DOCX: {file_path}")
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
                
            logger.info(f"Extracted {len(chunks)} chunks from {file_path}")
            self.add_documents(chunks, source=file_path)
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {e}")

    def load_youtube_video(self, url):
        """Extract transcript from YouTube video"""
        logger.info(f"Processing YouTube video: {url}")
        try:
            # Extract video ID from URL
            video_id = None
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
                r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    break
            
            if not video_id:
                logger.error("Could not extract video ID from URL")
                return
            
            logger.info(f"Extracted video ID: {video_id}")
            
            # Fetch transcript using the API
            try:
                api = YouTubeTranscriptApi()
                transcript_list = api.fetch(video_id)
            except Exception as transcript_error:
                error_msg = str(transcript_error)
                if "Could not retrieve" in error_msg or "transcript" in error_msg.lower():
                    logger.error(f"No transcripts available for this video")
                    print("\n❌ This video doesn't have transcripts enabled.")
                    print("   Try a different video with captions/subtitles available.")
                    return
                else:
                    raise
            
            # Combine transcript pieces into full text
            full_text = " ".join([entry.text for entry in transcript_list])
            
            logger.info(f"Retrieved transcript: {len(full_text)} characters")
            
            # Chunk the transcript
            chunks = []
            current_chunk = ""
            
            # Split by sentences
            sentences = re.split(r'(?<=[.!?])\s+', full_text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(current_chunk) + len(sentence) < 500:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    overlap = current_chunk[-50:] if len(current_chunk) > 50 else ""
                    current_chunk = overlap + sentence + " "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            logger.info(f"Extracted {len(chunks)} chunks from YouTube video")
            self.add_documents(chunks, source=f"YouTube: {url}")
            
        except Exception as e:
            logger.error(f"Error processing YouTube video: {e}")
            print(f"\n❌ Error: {str(e)}")
            return

    def retrieve(self, query, top_k=3):
        """Retrieve most relevant documents"""
        if self.doc_embeddings is None:
            return []
            
        query_embedding = self.encoder.encode([query])
        similarities = cosine_similarity(query_embedding, self.doc_embeddings)[0]
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                "score": similarities[idx],
                "document": self.documents[idx]
            })
        return results

    def generate_response(self, query, context):
        """Generate answer using LLM"""
        logger.info(f"Generating response with {self.llm_provider.upper()}...")
        
        prompt = f"""Answer the question based on the context below.
        
Context:
{context}

Question: {query}
Answer:"""
        
        try:
            if self.llm_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant. Answer questions based on the provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            elif self.llm_provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.llm_provider == 'google':
                response = self.client.generate_content(prompt)
                return response.text
            
            elif self.llm_provider == 'local':
                result = self.generator(prompt, max_new_tokens=200, do_sample=False)
                return result[0]['generated_text']
            
            else:
                return "Error: Invalid LLM provider"
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"

def main():
    rag = SimpleRAG()

    # Scan for DOCX files in current directory
    print("\nScanning for DOCX files...")
    found_docs = False
    for filename in os.listdir('.'):
        if filename.lower().endswith('.docx'):
            print(f"Found: {filename}")
            found_docs = True
    
    if not found_docs:
        print("No DOCX files found. You can add them later!")
    
    print("\n💡 TIP: Paste YouTube URLs or ask questions!")

    while True:
        print("\n" + "="*50)
        user_input = input("YouTube URL or Question (or 'quit'): ")
        if user_input.lower() in ['quit', 'exit']:
            break

        # Check if input is a YouTube URL
        youtube_patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)',
            r'youtube\.com'
        ]
        
        is_youtube_url = any(re.search(pattern, user_input, re.IGNORECASE) for pattern in youtube_patterns)
        
        if is_youtube_url:
            print("📺 Loading YouTube video...")
            rag.load_youtube_video(user_input)
            print("✅ Video added! Ask questions about it.")
            continue

        # It's a question
        print(f"🔍 Searching: {user_input}")
        
        # Retrieve
        retrieved_docs = rag.retrieve(user_input, top_k=3)
        
        if not retrieved_docs:
            print("❌ No documents in knowledge base. Add a YouTube video or DOCX file first!")
            continue
        
        context = ""
        print("\n📚 Retrieved chunks:")
        for i, doc in enumerate(retrieved_docs, 1):
            score = doc['score']
            snippet = doc['document'][:100]
            print(f"  {i}. {snippet}... (Score: {score:.4f})")
            context += doc['document'] + " "

        # Generate answer
        print("\n💡 Answer:")
        answer = rag.generate_response(user_input, context)
        print(answer)

if __name__ == "__main__":
    main()
