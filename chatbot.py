import os
from dotenv import load_dotenv
import google.generativeai as genai
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings

# --- Load environment variables ---
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Initialize Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Initialize Embeddings (same model used in preprocess.py) ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- Connect to Pinecone ---
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

print(f"Connected to Pinecone index: {PINECONE_INDEX}")

# --- Chat loop ---
while True:
    query = input("\nYou: ")
    if query.lower() in ["exit", "quit"]:
        break

    # Embed the user query
    query_vector = embeddings.embed_query(query)

    # Search top 3 results
    results = index.query(vector=query_vector, top_k=3, include_metadata=True)

    # Extract the top chunks
    contexts = [match['metadata']['text'] for match in results['matches']]
    context_text = "\n\n".join(contexts)

    # Build the prompt for Gemini
    prompt = f"Answer the question based on the following context:\n{context_text}\n\nQuestion: {query}"

    # Generate answer
    response = model.generate_content(prompt)
    print("\nAssistant:", response.text)
