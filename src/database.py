"""
database.py — SQLite database setup aur helper functions.
YouTube transcripts aur chunks ko permanently store karta hai.
"""

import sqlite3
import json
import os

# Database file ka path — project root mein banegi
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "./database/transcripts.db")


def get_connection() -> sqlite3.Connection:
    """Database connection lo. Row factory set karo taaki dict mile."""
    # 👉 YE NAYI LINE FOLDER BANAYEGI AGAR WO NAHI HAI
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """
    Tables banao agar exist nahi karte.
    App start hone par ek baar call hota hai.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Videos table — har processed video ka record
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            video_id    TEXT PRIMARY KEY,
            language    TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Transcript lines table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcript_lines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id    TEXT NOT NULL,
            start_time  REAL NOT NULL,
            duration    REAL NOT NULL,
            text        TEXT NOT NULL,
            FOREIGN KEY (video_id) REFERENCES videos(video_id)
        )
    """)

    # Chunks table — embeddings JSON mein store honge
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id     TEXT NOT NULL,
            chunk_index  INTEGER NOT NULL,
            start_time   REAL NOT NULL,
            end_time     REAL NOT NULL,
            text         TEXT NOT NULL,
            embedding    TEXT,          -- JSON array as string
            FOREIGN KEY (video_id) REFERENCES videos(video_id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database ready: {DB_PATH}")


# ─── Video ──────────────────────────────────────────────────────────────────

def video_exists(video_id: str) -> bool:
    """Check karo ki video already database mein hai ya nahi."""
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    conn.close()
    return row is not None


def save_video(video_id: str, language: str):
    """Video record save karo."""
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO videos (video_id, language) VALUES (?, ?)",
        (video_id, language)
    )
    conn.commit()
    conn.close()


# ─── Transcript ─────────────────────────────────────────────────────────────

def save_transcript(video_id: str, transcript: list):
    """
    Transcript lines bulk insert karo.
    transcript = [{'text': ..., 'start': ..., 'duration': ...}, ...]
    """
    conn = get_connection()
    rows = [
        (video_id, item["start"], item["duration"], item["text"])
        for item in transcript
    ]
    conn.executemany(
        "INSERT INTO transcript_lines (video_id, start_time, duration, text) VALUES (?, ?, ?, ?)",
        rows
    )
    conn.commit()
    conn.close()


def load_transcript(video_id: str) -> list:
    """
    Database se transcript load karo.
    Returns: [{'text': ..., 'start': ..., 'duration': ...}, ...]
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT text, start_time, duration FROM transcript_lines WHERE video_id = ? ORDER BY start_time",
        (video_id,)
    ).fetchall()
    conn.close()
    return [
        {"text": r["text"], "start": r["start_time"], "duration": r["duration"]}
        for r in rows
    ]


# ─── Chunks ─────────────────────────────────────────────────────────────────

def save_chunks(video_id: str, chunks: list):
    """
    Chunks bulk insert karo (embedding JSON mein convert karke).
    chunks = [{'chunk_index': ..., 'start_time': ..., 'end_time': ..., 'text': ..., 'embedding': [...]}, ...]
    """
    conn = get_connection()
    rows = []
    for chunk in chunks:
        embedding_json = json.dumps(chunk["embedding"]) if chunk.get("embedding") else None
        rows.append((
            video_id,
            chunk["chunk_index"],
            chunk["start_time"],
            chunk["end_time"],
            chunk["text"],
            embedding_json
        ))
    conn.executemany(
        """INSERT INTO chunks
           (video_id, chunk_index, start_time, end_time, text, embedding)
           VALUES (?, ?, ?, ?, ?, ?)""",
        rows
    )
    conn.commit()
    conn.close()


def load_chunks(video_id: str) -> list:
    """
    Database se chunks load karo (embedding JSON parse karke).
    Returns list of chunk dicts — same format jo embed_data.py use karta hai.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT chunk_index, start_time, end_time, text, embedding
           FROM chunks WHERE video_id = ? ORDER BY chunk_index""",
        (video_id,)
    ).fetchall()
    conn.close()

    chunks = []
    for r in rows:
        chunks.append({
            "chunk_index": r["chunk_index"],
            "start_time":  r["start_time"],
            "end_time":    r["end_time"],
            "text":        r["text"],
            "embedding":   json.loads(r["embedding"]) if r["embedding"] else None,
        })
    return chunks


def chunks_have_embeddings(video_id: str) -> bool:
    """Check karo ki chunks ke embeddings saved hain ya nahi."""
    conn = get_connection()
    row = conn.execute(
        "SELECT embedding FROM chunks WHERE video_id = ? LIMIT 1",
        (video_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return False
    return row["embedding"] is not None
