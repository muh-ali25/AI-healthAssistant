import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in .env")

if not PINECONE_INDEX:
    raise ValueError("PINECONE_INDEX not found in .env")

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if PINECONE_INDEX not in [idx.name for idx in pc.list_indexes()]:
    print(f"Creating new Pinecone index: {PINECONE_INDEX}")
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=384,  # or 768 if you used a larger embedding model
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Connect to index
index = pc.Index(PINECONE_INDEX)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def query_top_k(query: str, k: int = 3):
    """
    Query Pinecone index for top-k relevant documents.
    Returns a list of matches: [{id, score, text}]
    """
    if not query or not query.strip():
        return []

    # Convert text query into vector embedding
    query_emb = model.encode(query).tolist()

    # Perform query
    res = index.query(vector=query_emb, top_k=k, include_metadata=True)

    # Normalize results
    matches = []
    for match in res.get("matches", []):
        matches.append({
            "id": match.get("id"),
            "score": match.get("score"),
            "text": match.get("metadata", {}).get("text", "")
        })

    return matches
