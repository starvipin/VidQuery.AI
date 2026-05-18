"""
3_merge_chunks.py — Transcript lines ko meaningful chunks mein merge karo.
Har chunk ka start_time track hota hai taaki timestamp accurate rahe.
(Database dependency removed)
"""

import json
import os

# Ek chunk mein kitne words honge (approximate)
# Ek chunk mein kitne words honge (approximate) - 150 ki jagah 70 kar dein
CHUNK_SIZE_WORDS = 70
# Do chunks ke beech kitna overlap (words) - thoda kam kar dein
CHUNK_OVERLAP_WORDS = 15


def merge_transcript_into_chunks(transcript: list, chunk_size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP_WORDS) -> list:
    """
    Transcript lines ko fixed-size word chunks mein merge karo.
    
    Args:
        transcript: [{'text': ..., 'start': ..., 'duration': ...}, ...]
        chunk_size: Ek chunk mein maximum words
        overlap: Consecutive chunks ke beech shared words
    
    Returns:
        [{'chunk_index': 0, 'start_time': 0.0, 'end_time': 30.0, 'text': '...'}, ...]
    """
    if not transcript:
        return []

    # Pehle words ki list banao with unka timestamp
    word_tokens = []  # [{'word': ..., 'start': ..., 'end': ...}]
    
    for item in transcript:
        text = item.get("text", "").strip()
        start = float(item.get("start", 0))
        duration = float(item.get("duration", 0))
        words = text.split()
        if not words:
            continue
        
        # Words ko evenly distribute karo line ke duration mein
        per_word_time = duration / len(words) if len(words) > 0 else 0
        for i, word in enumerate(words):
            word_tokens.append({
                "word": word,
                "start": start + i * per_word_time,
                "end": start + (i + 1) * per_word_time,
            })

    if not word_tokens:
        return []

    chunks = []
    chunk_index = 0
    i = 0

    while i < len(word_tokens):
        # Is chunk ke words
        chunk_words = word_tokens[i : i + chunk_size]
        
        chunk_text = " ".join(w["word"] for w in chunk_words)
        chunk_start = chunk_words[0]["start"]
        chunk_end = chunk_words[-1]["end"]

        chunks.append({
            "chunk_index": chunk_index,
            "start_time": round(chunk_start, 2),
            "end_time": round(chunk_end, 2),
            "text": chunk_text,
            "embedding": None,  # baad mein fill hoga
        })

        chunk_index += 1
        # Overlap ke liye thoda peeche jao
        step = chunk_size - overlap
        i += max(step, 1)

    return chunks


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
    # Database nahi hai, toh testing ke liye ek dummy transcript banaya hai
    dummy_transcript = [
        {"text": "Hello and welcome to this video about python programming.", "start": 0.0, "duration": 4.0},
        {"text": "Today we will learn how to process transcripts properly.", "start": 4.5, "duration": 4.0},
        {"text": "Let's divide them into manageable text chunks.", "start": 9.0, "duration": 3.0}
    ]
    
    print("🔪 Processing dummy transcript data...")
    # Demo ke liye chunk size chhota rakha hai
    chunks = merge_transcript_into_chunks(dummy_transcript, chunk_size=6, overlap=2)

    if chunks:
        print(f"\n📦 Total chunks: {len(chunks)}\n")
        for chunk in chunks:
            print(f"Chunk #{chunk['chunk_index']} | [{format_time(chunk['start_time'])} → {format_time(chunk['end_time'])}]")
            print(f"  {chunk['text']}")
            print()
    else:
        print("❌ Koi chunks nahi bane.")