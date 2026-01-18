import sqlite3
import json
import logging
import os

logger = logging.getLogger(__name__)

class KnowledgeDB:
    def __init__(self, db_path="knowledge_base.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for documents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for embeddings (stored as JSON string since SQLite doesn't have vector type by default)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                doc_id INTEGER,
                embedding TEXT,
                FOREIGN KEY(doc_id) REFERENCES documents(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_document(self, content, source, embedding_list):
        """
        Adds a document and its embedding to the database.
        embedding_list: list of floats (the vector)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert doc
            cursor.execute('INSERT INTO documents (content, source) VALUES (?, ?)', (content, source))
            doc_id = cursor.lastrowid
            
            # Insert embedding
            # Convert numpy array or list to JSON string
            emb_json = json.dumps(embedding_list)
            cursor.execute('INSERT INTO embeddings (doc_id, embedding) VALUES (?, ?)', (doc_id, emb_json))
            
            conn.commit()
            conn.close()
            return doc_id
        except Exception as e:
            logger.error(f"DB Error adding document: {e}")
            return None

    def get_all_documents(self):
        """
        Retrieves all documents and embeddings to load into memory on startup.
        Returns: list of dicts {id, content, source, embedding}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.id, d.content, d.source, e.embedding 
            FROM documents d 
            JOIN embeddings e ON d.id = e.doc_id
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "content": r[1],
                "source": r[2],
                "embedding": json.loads(r[3])
            })
            
        return results

    def clear(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents")
        cursor.execute("DELETE FROM embeddings")
        conn.commit()
        conn.close()
