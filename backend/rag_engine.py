"""
RAG Engine - Core retrieval and generation logic
Uses LangChain + ChromaDB + OpenAI
"""

import os
from pathlib import Path
from typing import Optional

from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate


SYSTEM_PROMPT = """You are an intelligent document assistant. 
Answer questions based ONLY on the provided document context.
If the answer is not in the document, say "I couldn't find that in the document."
Be concise, accurate, and helpful.

Context: {context}
Chat History: {chat_history}
Question: {question}
Answer:"""


class RAGEngine:
    def __init__(self, openai_api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.2,
            openai_api_key=openai_api_key
        )
        self.vectorstore = None
        self.chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

    def load_document(self, file_path: str) -> int:
        """Load, chunk and embed a document. Returns chunk count."""
        path = Path(file_path)
        ext = path.suffix.lower()

        # Load based on file type
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".txt":
            loader = TextLoader(file_path)
        elif ext in [".docx", ".doc"]:
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        documents = loader.load()

        # Smart chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=80,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = splitter.split_documents(documents)

        # Embed and store
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name="rag_docs"
        )

        # Build conversational chain
        prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=SYSTEM_PROMPT
        )

        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 4, "fetch_k": 8}
            ),
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": prompt}
        )

        return len(chunks)

    def ask(self, question: str) -> dict:
        """Ask a question and return answer + sources."""
        if not self.chain:
            return {"answer": "Please upload a document first.", "sources": []}

        result = self.chain({"question": question})

        sources = []
        for doc in result.get("source_documents", []):
            page = doc.metadata.get("page", "N/A")
            snippet = doc.page_content[:150].strip()
            sources.append({"page": page, "snippet": snippet})

        return {
            "answer": result["answer"],
            "sources": sources
        }

    def reset(self):
        """Clear memory and vectorstore for new document."""
        self.memory.clear()
        if self.vectorstore:
            self.vectorstore.delete_collection()
        self.vectorstore = None
        self.chain = None
