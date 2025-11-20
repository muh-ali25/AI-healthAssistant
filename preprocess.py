import os
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_core.documents import Document
from langchain.schema import Document 

from tqdm import tqdm

# Load .env
load_dotenv()

# Pinecone / Gemini keys are in .env
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Step 1: Load all PDFs from 'data/' folder
pdf_folder = "data"
pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

texts = []

for file in pdf_files:
    reader = PdfReader(file)
    for page in reader.pages:
        texts.append(page.extract_text())

print(f"Loaded {len(texts)} pages from {len(pdf_files)} PDFs.")

# Step 2: Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = []
for t in texts:
    chunks.extend(text_splitter.split_text(t))


print(f"Total chunks created: {len(chunks)}")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# Test with a small batch first
# chunks = chunks[:10]  # optional, for testing
embs = embeddings.embed_documents(chunks)

print(f"Generated embeddings for {len(embs)} chunks.")

documents = [Document(page_content=chunk) for chunk in chunks]
print(f"Prepared {len(documents)} documents for Pinecone upload.")

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = PINECONE_INDEX

# Check if index exists; if not, create it
if index_name not in [i.name for i in pc.list_indexes()]:
    print(f"Creating Pinecone index '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=384,  # for all-MiniLM-L6-v2
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
else:
    print(f"Using existing Pinecone index '{index_name}'")
    
index = pc.Index(index_name)

print("Uploading embeddings to Pinecone...")

vectors = []
for i, doc in enumerate(documents):
    vectors.append({
        "id": f"doc-{i}",
        "values": embeddings.embed_query(doc.page_content),
        "metadata": {"text": doc.page_content}
    })

#index.upsert(vectors=vectors)

batch_size = 100  # you can adjust this to 50 or 100 depending on vector size
for i in range(0, len(vectors), batch_size):
    batch = vectors[i:i + batch_size]
    index.upsert(vectors=batch)
    print(f" Uploaded batch {i // batch_size + 1} ({len(batch)} vectors)")\
        
print(f" Uploaded {len(vectors)} vectors to Pinecone index '{index_name}'.")

