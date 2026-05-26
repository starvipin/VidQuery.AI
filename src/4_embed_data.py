"""
4_embed_data.py — Chunks ke OpenAI embeddings generate karo (Database dependency removed).
Phir cosine similarity se relevant chunks dhundo question ke liye.
"""

import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100  # OpenAI API ek baar mein kitne texts embed kare


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable set nahi hai.")
    return OpenAI(api_key=api_key)


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    OpenAI se batch mein embeddings lo.
    Returns list of embedding vectors.
    """
    # Empty strings hata do
    clean_texts = [t.strip() if t.strip() else "empty" for t in texts]
    
    response = get_openai_client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=clean_texts,
    )
    return [item.embedding for item in response.data]


def embed_chunks(chunks: list) -> list:
    """
    Diye gaye chunks list ke embeddings generate karo aur unme add karo.
    
    Args:
        chunks: List of chunk dictionaries.
    
    Returns:
        List of chunks jisme 'embedding' add ho gayi hai.
    """
    if not chunks:
        print("Koi chunks nahi mile embed karne ke liye.")
        return []

    print(f"{len(chunks)} chunks ke embeddings generate ho rahe hain...")

    # Batch mein embed karo
    texts = [chunk["text"] for chunk in chunks]
    all_embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} chunks...")
        embeddings = get_embeddings_batch(batch)
        all_embeddings.extend(embeddings)

    # Chunks mein embedding set karo
    for chunk, embedding in zip(chunks, all_embeddings):
        chunk["embedding"] = embedding

    print(f"{len(chunks)} chunks ke embeddings generate ho gaye.")
    return chunks


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """Do vectors ke beech cosine similarity calculate karo"""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def find_relevant_chunks(question: str, chunks: list, top_k: int = 4) -> list:
    """
    Question ke liye sabse relevant chunks dhundo (semantic search).
    
    Args:
        question: User ka sawal.
        chunks: Already embedded chunks ki list.
        top_k: Kitne results chahiye.
        
    Returns: 
        top_k chunks sorted by relevance
    """
    if not chunks:
        return []

    # Question ka embedding lo
    question_emb = get_embeddings_batch([question])[0]

    # Har chunk ke saath similarity calculate karo
    scored = []
    for chunk in chunks:
        if not chunk.get("embedding"):
            continue
        score = cosine_similarity(question_emb, chunk["embedding"])
        scored.append({
            "chunk_index": chunk["chunk_index"],
            "start_time": chunk["start_time"],
            "end_time": chunk["end_time"],
            "text": chunk["text"],
            "score": round(score, 4),
        })

    # Score ke hisab se sort karo
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def format_time(seconds: float) -> str:
    """Seconds ko MM:SS ya HH:MM:SS format mein convert karo"""
    secs = int(seconds)
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    sec = secs % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


# ─────── Direct run karne ke liye ───────
if __name__ == "__main__":
    # Test karne ke liye dummy data (Database ka kaam khatam)
    dummy_chunks = [
        {"chunk_index": 0, "start_time": 0.0, "end_time": 5.0, "text": "Python is a popular programming language.", "embedding": None},
        {"chunk_index": 1, "start_time": 5.0, "end_time": 10.0, "text": "Machine learning relies on processing large datasets.", "embedding": None},
        {"chunk_index": 2, "start_time": 10.0, "end_time": 15.0, "text": "We use OpenAI API to generate text embeddings.", "embedding": None}
    ]
    
    print("Dummy chunks ke embeddings generate kar rahe hain (OpenAI API key zaroori hai)...")
    try:
        # Pura process variables (lists) par chalega, DB par nahi
        embedded_chunks = embed_chunks(dummy_chunks)
        
        if embedded_chunks:
            question = input("\nKoi sawal poocho (e.g. 'What is used for embeddings?'): ").strip()
            if question:
                results = find_relevant_chunks(question, embedded_chunks)
                print(f"\n🔍 Top {len(results)} relevant chunks:\n")
                
                for r in results:
                    print(f"[Score: {r['score']}] [{format_time(r['start_time'])}] {r['text']}")
    except Exception as e:
        print(f"Error aaya (Shayad aapki OpenAI API key set nahi hai): {e}")
