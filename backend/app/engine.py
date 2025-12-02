# engine.py
import os
import logging
import numpy as np
import faiss
from typing import List

from app.db import get_mongo_client
from app.config import settings
import google.generativeai as genai

import docx2txt  
from pypdf import PdfReader

logger = logging.getLogger("policy_ai.engine")
logger.setLevel(logging.INFO)

# 1. Setup Gemini
if not settings.GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not set in environment!")

genai.configure(api_key=settings.GEMINI_API_KEY)

# Constants
GEN_MODEL = "gemini-2.0-flash"
EMBED_MODEL = "models/text-embedding-004" # Updated to the stable model name

# Index path
INDEX_DIR = "./indexes"
os.makedirs(INDEX_DIR, exist_ok=True)

def _index_path(company_id: str):
    # Sanitize the filename
    safe = "".join(c if c.isalnum() else "_" for c in company_id)
    return os.path.join(INDEX_DIR, f"{safe}.index")

# MongoDB Collection
def meta_coll():
    return get_mongo_client()[settings.DB_NAME][settings.COLLECTION_NAME]

# ---------- Read & Chunk ----------
def _read_text_file(path):
    """
    Intelligently extracts text from PDF, DOCX, and TXT files.
    """
    ext = os.path.splitext(path)[1].lower()
    
    try:
        # 1. Handle PDF
        if ext == ".pdf":
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
            
        # 2. Handle Word Documents (.docx)
        elif ext == ".docx":
            # docx2txt extracts all text including headers/footers
            return docx2txt.process(path)

        # 3. Handle Text / Markdown
        elif ext in [".txt", ".md", ".csv"]:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
                
        # 4. Unknown Format
        else:
            print(f"⚠️ Unsupported format: {ext}")
            return ""
                
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return ""

def _chunk(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

# ---------- Embeddings ----------
def _embed(texts: List[str]) -> np.ndarray:
    """Generates embeddings using Gemini."""
    if not texts:
        return np.array([])
    
    try:
        # Batch embedding is faster
        result = genai.embed_content(
            model=EMBED_MODEL,
            content=texts,
            task_type="retrieval_document"
        )
        
        # Handle different API response structures
        if 'embedding' in result:
            vecs = [result['embedding']]
        elif 'embeddings' in result:
            vecs = result['embeddings']
        else:
            vecs = []

        arr = np.array(vecs, dtype=np.float32)
        
        # --- FIX: DEBUG & CORRECT SHAPE ---
        print(f"📐 DEBUG: Original Embedding Shape: {arr.shape}")
        
        # If shape is (1, N, 768) or similar, flatten it to (N, 768)
        if arr.ndim > 2:
            arr = np.squeeze(arr)
            print(f"📐 DEBUG: Fixed Embedding Shape: {arr.shape}")
            
        # If shape is (768,), make it (1, 768)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        # ----------------------------------

        # Normalize for Cosine Similarity
        faiss.normalize_L2(arr)
        return arr
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise e

# ---------- FAISS Operations ----------
def create_index(file_path: str, company_id: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # 1. Read and Chunk
    text = _read_text_file(file_path)
    chunks = _chunk(text)
    
    if not chunks:
        return "File was empty or could not be read."

    print(f"📄 Processing {len(chunks)} chunks for company {company_id}...")

    # 2. Embed
    vecs = _embed(chunks)
    if vecs.size == 0:
        return "Failed to generate embeddings."

    # 3. Save Metadata to MongoDB (Store the actual text)
    coll = meta_coll()
    # Clean up old data for this file if needed, or append.
    # For now, we append.
    
    docs = []
    filename = os.path.basename(file_path)
    
    # We use a unique ID for the vector to map back to text
    start_id = 0
    if os.path.exists(_index_path(company_id)):
         old_idx = faiss.read_index(_index_path(company_id))
         start_id = old_idx.ntotal

    ids = np.arange(start_id, start_id + len(chunks)).astype('int64')

    for i, chunk in enumerate(chunks):
        docs.append({
            "vec_id": int(ids[i]),
            "company_id": company_id,
            "filename": filename,
            "text": chunk
        })
    
    coll.insert_many(docs)

    # 4. Save Vectors to FAISS (Local File)
    dim = vecs.shape[1]
    idx_path = _index_path(company_id)
    
    if os.path.exists(idx_path):
        index = faiss.read_index(idx_path)
    else:
        # Create new index (Inner Product = Cosine Similarity because we normalized)
        index = faiss.IndexFlatIP(dim)
        # We need IDMap to track specific IDs
        index = faiss.IndexIDMap(index)

    index.add_with_ids(vecs, ids)
    faiss.write_index(index, idx_path)

    return f"Successfully indexed {len(chunks)} text chunks."

def get_chat_engine(company_id):
    return ChatEngine(company_id)

class ChatEngine:
    def __init__(self, company_id):
        self.company_id = company_id
        self.idx_path = _index_path(company_id)

    def chat(self, question: str):
        # 1. Search Vector DB
        context_text = ""
        sources = set()
        score = 0.0

        if os.path.exists(self.idx_path):
            q_vec = _embed([question])
            index = faiss.read_index(self.idx_path)
            D, I = index.search(q_vec, 3) # Top 3 chunks
            
            indices = I[0]
            scores = D[0]
            score = float(scores[0]) if len(scores) > 0 else 0

            coll = meta_coll()
            found_chunks = []
            for idx in indices:
                if idx == -1: continue
                doc = coll.find_one({"vec_id": int(idx), "company_id": self.company_id})
                if doc:
                    found_chunks.append(doc['text'])
                    sources.add(doc['filename'])
            
            context_text = "\n\n".join(found_chunks)

        # 2. The "Dual Brain" Prompt
        # This tells Gemini: "If asked to write, WRITE. If asked for facts, check Policy."
        prompt = f"""
        You are an intelligent HR Policy Assistant. 
        
        ### SOURCES (Company Policy):
        {context_text}

        ### USER REQUEST:
        {question}

        ### INSTRUCTIONS:
        1. **Task Execution:** If the user asks you to write an email, letter, or draft, YOU MUST DO IT. 
           - Use the SOURCES to check for rules (e.g., notice period, who to CC).
           - If the policy doesn't say, use standard professional placeholders like [Manager Name].
        
        2. **Fact Checking:** If the user asks a specific question (e.g., "How many leaves?"), answer strictly from the SOURCES. 
           - If the answer is not in the SOURCES, say "I cannot find that information in the policy."

        3. **Tone:** Professional, helpful, and concise.

        Answer now:
        """

        # 3. Call Gemini
        model = genai.GenerativeModel(GEN_MODEL)
        response = model.generate_content(prompt)

        return type("Response", (), {
            "response": response.text, 
            "sources": list(sources), 
            "score": score
        })