import numpy as np
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader
from docx import Document
from db import KnowledgeDB
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi
import re


import logging
import sys

import logging
import sys
from duckduckgo_search import DDGS
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SimpleRAG:
    def __init__(self):
        logger.info("Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Configure LLM provider
        self.llm_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
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
            logger.warning(f"Unknown provider '{self.llm_provider}', falling back to OpenAI")
            self._init_openai()

        # Vision Model (Lazy load or init here - simplified to use BLIP for image captioning)
        # We won't load it immediately to save startup time, or we can catch it later.
        self.vision_processor = None
        self.vision_model = None
        
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
                logger.error("OpenAI API key not set! Please set OPENAI_API_KEY in .env file")
                logger.info("Falling back to local model...")
                self._init_local_model()
                return
            
            self.client = OpenAI(api_key=api_key)
            self.model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            logger.info(f"✅ OpenAI initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            logger.info("Falling back to local model...")
            self._init_local_model()
    
    def _init_anthropic(self):
        """Initialize Anthropic Claude LLM"""
        try:
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key or api_key == 'your-anthropic-api-key-here':
                logger.error("Anthropic API key not set! Please set ANTHROPIC_API_KEY in .env file")
                logger.info("Falling back to local model...")
                self._init_local_model()
                return
            
            self.client = Anthropic(api_key=api_key)
            self.model_name = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
            logger.info(f"✅ Anthropic initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic: {e}")
            logger.info("Falling back to local model...")
            self._init_local_model()
    
    def _init_google(self):
        """Initialize Google Gemini LLM"""
        try:
            import google.generativeai as genai
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key or api_key == 'your-google-api-key-here':
                logger.error("Google API key not set! Please set GOOGLE_API_KEY in .env file")
                logger.info("Falling back to local model...")
                self._init_local_model()
                return
            
            genai.configure(api_key=api_key)
            self.model_name = os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash-exp')
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"✅ Google Gemini initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Google Gemini: {e}")
            logger.info("Falling back to local model...")
            self._init_local_model()
    
    def _init_local_model(self):
        """Initialize local flan-t5-base model"""
        logger.info("Loading local model (google/flan-t5-base)...")
        from transformers import pipeline
        self.generator = pipeline(
            "text2text-generation", 
            model="google/flan-t5-base", 
            device_map="auto"
        )
        self.llm_provider = 'local'
        logger.info("✅ Local model loaded successfully")


    def load_from_db(self):
        logger.info("Loading knowledge from database...")
        records = self.db.get_all_documents()
        if records:
            self.documents = [r['content'] for r in records]
            embeddings = [r['embedding'] for r in records]
            self.doc_embeddings = np.array(embeddings)
            logger.info(f"Loaded {len(records)} documents from DB.")
        else:
            logger.info("Database is empty.")

    def add_documents(self, docs, source="unknown"):
        """
        Adds new documents to the existing knowledge base and saves to DB.
        """
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
            
        logger.info(f"Total documents in knowledge base: {len(self.documents)}")

    def load_pdf(self, file_path):
        """
        Reads a PDF file and chunks the text into smaller pieces for embedding.
        Uses a sliding window approach with sentence/paragraph preservation where possible.
        """
        logger.info(f"Processing PDF: {file_path}")
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
            

            
            
            logger.info(f"Extracted {len(chunks)} chunks from {file_path}")
            self.add_documents(chunks, source=file_path)
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")

    def load_docx(self, file_path):
        """
        Reads a DOCX file and chunks the text.
        """
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
        """
        Extracts transcript from a YouTube video and adds it to the knowledge base.
        Supports various YouTube URL formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://m.youtube.com/watch?v=VIDEO_ID
        """
        logger.info(f"Processing YouTube video: {url}")
        try:
            # Extract video ID from URL using regex
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
            
            # Fetch transcript - use list_transcripts() and get manually transcribed or auto-generated
            from youtube_transcript_api import YouTubeTranscriptApi as YT_API
            transcript_list = YT_API.get_transcript(video_id)
            
            # Combine transcript pieces into full text
            full_text = " ".join([entry['text'] for entry in transcript_list])
            
            logger.info(f"Retrieved transcript with {len(full_text)} characters")
            
            # Chunk the transcript similar to how we chunk PDFs
            chunks = []
            current_chunk = ""
            
            # Split by sentences for better chunking
            sentences = re.split(r'(?<=[.!?])\s+', full_text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Add sentence to current chunk
                if len(current_chunk) + len(sentence) < 500:
                    current_chunk += sentence + " "
                else:
                    # Chunk is full, save it
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    overlap = current_chunk[-50:] if len(current_chunk) > 50 else ""
                    current_chunk = overlap + sentence + " "
            
            # Add the last chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            logger.info(f"Extracted {len(chunks)} chunks from YouTube video")
            self.add_documents(chunks, source=f"YouTube: {url}")
            
        except Exception as e:
            logger.error(f"Error processing YouTube video {url}: {e}")
            return f"Error: {str(e)}"


    def analyze_image(self, image_path):
        """
        Uses Salesforce/blip-image-captioning-base to generate a description of the image.
        """
        logger.info(f"Analyzing image: {image_path}")
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            
            if self.vision_model is None:
                logger.info("Loading Vision Model (BLIP)...")
                self.vision_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.vision_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            raw_image = Image.open(image_path).convert('RGB')
            inputs = self.vision_processor(raw_image, return_tensors="pt")
            out = self.vision_model.generate(**inputs)
            caption = self.vision_processor.decode(out[0], skip_special_tokens=True)
            
            return caption
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Error analyzing image: {str(e)}"

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
        logger.info(f"Generating response with {self.llm_provider.upper()} LLM...")
        
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
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            
            elif self.llm_provider == 'google':
                response = self.client.generate_content(prompt)
                return response.text
            
            elif self.llm_provider == 'local':
                # Local flan-t5-base model
                result = self.generator(prompt, max_new_tokens=200, do_sample=False)
                return result[0]['generated_text']
            
            else:
                logger.error(f"Unknown LLM provider: {self.llm_provider}")
                return "Error: Invalid LLM provider configured"
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"


def main():
    rag = SimpleRAG()

    # 1. Add default knowledge
    # 1. Add default knowledge ONLY if DB is empty to avoid duplicates
    if len(rag.documents) == 0:
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
    # Only load files if their content isn't already in the DB (deduplication logic is simple here)
    print("\nScanning for documents in current directory...")
    found_docs = False
    for filename in os.listdir('.'):
        if filename.lower().endswith('.pdf') or filename.lower().endswith('.docx'):
            # In a real app we'd check file hashes or paths in DB. 
            # For now, we rely on the `reload_documents` tool or manual invocation.
            # But since this is the interactive script, let's load them to ensure they are in DB.
            # Optimally we should check if they exist in DB first, but SimpleRAG.load_* methods
            # in this version just blindly add. 
            # To avoid extensive refactoring, let's trust the user or the DB wrapper.
            # Actually, let's just NOT auto-load here if we already have documents?
            # No, if we have new files we want them.
            pass
            
    # For the interactive script, let's just rely on what's in the DB + explicit user drag/drop in future.
    # But to match previous behavior:
    # If the user put files in the folder, they expect them to be loaded.
    # The `load_pdf` function now saves to DB. 
    # To prevent duplicates, we should clear DB or check existence.
    # Simplest Fix: Don't auto-scan here. Rely on what was loaded from DB.
    # If user wants to ingest, they should use the MCP tool `reload_documents` or we add a command here.
    pass
    
    if not found_docs:
        print("No PDF or DOCX files found. Drop files in this folder to index them!")
    
    print("\n💡 TIP: You can also paste YouTube URLs directly to add video transcripts!")

    while True:
        print("\n" + "="*50)
        user_query = input("Enter your question or YouTube URL (or 'quit' to exit): ")
        if user_query.lower() in ['quit', 'exit']:
            break

        # Check if input is a YouTube URL
        youtube_patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)',
            r'youtube\.com'
        ]
        
        is_youtube_url = any(re.search(pattern, user_query, re.IGNORECASE) for pattern in youtube_patterns)
        
        if is_youtube_url:
            print(f"📺 Detected YouTube URL! Processing video transcript...")
            rag.load_youtube_video(user_query)
            print("✅ Video transcript added to knowledge base!")
            print("   You can now ask questions about this video.")
            continue

        print(f"Searching for: {user_query}")
        
        
        
        # Retrieve
        retrieved_docs = rag.retrieve(user_query, top_k=3)
        
        context = ""
        max_score = 0
        
        print("\n[Retrieved Context]:")
        for doc in retrieved_docs:
            score = doc['score']
            if score > max_score:
                max_score = score
            snippet = doc['document'].replace('\n', ' ')[:100] + "..."
            print(f"- {snippet} (Score: {score:.4f})")
            
            # Initial context load - we might clear this if web search is needed
            context += doc['document'] + " "

        # Web Search Fallback controls
        # Increased threshold to 0.35 because 0.26 was a false positive for "cm of tn"
        WEB_SEARCH_THRESHOLD = 0.35
        
        if max_score < WEB_SEARCH_THRESHOLD:
            print(f"\n[Low confidence locally (Highest: {max_score:.4f})]. Searching Web...")
            
            # If local score is REALLY low (< 0.2), discard local context to save tokens for web
            if max_score < 0.2:
                context = ""
                
            try:
                # Retrieve slightly more results to ensure quality
                web_results = DDGS().text(user_query, max_results=5)
                if web_results:
                    print(f"Found {len(web_results)} web results.")
                    for r in web_results:
                        # Add web content to context
                        # Format clearly so LLM distinguishes sources
                        web_context = f" [Web Info: {r['title']} - {r['body']}] "
                        context += web_context
                        print(f"- [Web] {r['title']}")
                else:
                     print("Web search returned no results.")
            except Exception as e:
                print(f"Web search failed: {e}")

        # TRUNCATE CONTEXT to fit usage limits of flan-t5-base (approx 512 tokens)
        # 1 token ~= 4 chars. Safe limit: 1500 chars to leave room for prompt + generation.
        if len(context) > 1500:
            print(f"\n[Warning] Context too long ({len(context)} chars). Truncating to 1500...")
            context = context[:1500]

        # Generate
        print("\n[LLM Answer]:")
        answer = rag.generate_response(user_query, context)
        print(answer)

if __name__ == "__main__":
    main()
