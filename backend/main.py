# backend/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# load environment variables from project root .env by default
load_dotenv()

app = FastAPI(title="AI Health Assistant - Backend")

# env keys we expect (make sure they exist in your root .env)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.0")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# NOTE: these two service modules will be created in the next steps
# They encapsulate Pinecone retrieval and Gemini calling logic.
# For now we import them — you'll add them immediately afterwards.
from backend.services.pinecone_service import query_top_k
from backend.services.gemini_service import ask_gemini



# Allow React dev server origin (update if you host elsewhere)
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str
    top_k: int = 3

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(q: Question):
    # 1) Retrieve top-k contexts from Pinecone
    matches = query_top_k(q.question, k=q.top_k)  # returns list of {"id","score","text"}
    context_text = "\n\n".join([m["text"] for m in matches if m.get("text")])

    # 2) Build instruction prompt for Gemini
    prompt = f"""
You are a helpful, concise AI Health Assistant.
First, use the provided context to answer the question if it contains relevant information.
If the context does not contain enough information, use your own medical knowledge to give a clear and accurate answer."

Context:
{context_text}

Question:
{q.question}

Answer concisely and factually.
"""

    # 3) Call Gemini service
    answer = ask_gemini(prompt)

    # Return answer and the retrieved matches (useful for debugging / UI)
    return {"answer": answer, "matches": matches}


@app.get("/test_query")
def test_query(q: str = "what is diabetes"):
    results = query_top_k(q)
    return {"query": q, "results": results} 