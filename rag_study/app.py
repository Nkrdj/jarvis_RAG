import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List
import uvicorn
from simple_rag import SimpleRAG

app = FastAPI()

# Initialize RAG engine
print("Initializing RAG Engine...")
rag = SimpleRAG()

# Initial scan of directory
print("Scanning for existing documents...")
for filename in os.listdir('.'):
    if filename.lower().endswith('.pdf'):
        rag.load_pdf(filename)
    elif filename.lower().endswith('.docx'):
        rag.load_docx(filename)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.post("/query")
async def query_rag(request: QueryRequest):
    print(f"Received query: {request.query}")
    results = rag.retrieve(request.query, top_k=3)
    
    context_text = ""
    context_items = []
    
    for doc in results:
        # Keep track of context for the LLM
        context_text += doc['document'] + " "
        
        # Prepare context for the UI
        score = float(doc['score'])
        text_preview = doc['document'][:200] + "..." if len(doc['document']) > 200 else doc['document']
        context_items.append({
            "text": text_preview,
            "full_text": doc['document'],
            "score": score
        })
    
    answer = rag.generate_response(request.query, context_text)
    
    return {
        "answer": answer,
        "context": context_items
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = f"./{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
            
        if file.filename.lower().endswith('.pdf'):
            rag.load_pdf(file_location)
        elif file.filename.lower().endswith('.docx'):
            rag.load_docx(file_location)
        else:
            os.remove(file_location)
            return JSONResponse(status_code=400, content={"message": "Unsupported file type. Please upload PDF or DOCX."})
            
        return {"message": f"Successfully processed {file.filename}", "total_docs": len(rag.documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
