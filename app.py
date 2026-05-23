"""
app.py — Flask application entry point
YouTube CC + AI Q&A with timestamps using SQLite Database
"""

import os
import sys
import importlib.util
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-this")

# Initialize OpenAI Client
def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable set nahi hai.")
    return OpenAI(api_key=api_key)


# ─── Custom Module Loader ────────────────────────────────────────────────────
def _load(rel_path, module_name):
    spec = importlib.util.spec_from_file_location(
        module_name,
        os.path.join(os.path.dirname(__file__), rel_path)
    )
    
    # Linter (VS Code) ko satisfy karne ke liye None check
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot find or load module: {module_name} at {rel_path}")

    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


# Loading custom modules
_t = _load("src/5_get_transcript.py", "get_transcript_mod")
get_transcript_for_url          = _t.get_transcript_for_url
format_transcript_with_timestamps = _t.format_transcript_with_timestamps
extract_video_id                  = _t.extract_video_id

_m = _load("src/3_merge_chunks.py", "merge_chunks_mod")
merge_transcript_into_chunks  = _m.merge_transcript_into_chunks
format_time                   = _m.format_time

_e = _load("src/4_embed_data.py", "embed_data_mod")
embed_chunks                  = _e.embed_chunks
find_relevant_chunks          = _e.find_relevant_chunks

# Database module
_db = _load("src/database.py", "database_mod")
initialize_db           = _db.initialize_db
video_exists            = _db.video_exists
save_video              = _db.save_video
save_transcript         = _db.save_transcript
load_transcript         = _db.load_transcript
save_chunks             = _db.save_chunks
load_chunks             = _db.load_chunks
chunks_have_embeddings  = _db.chunks_have_embeddings

# App start hone par database tables banao
initialize_db()


# ─── Routes ─────────────────────────────────────────────────────────────────
@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler — JSON response dega HTML ki jagah."""
    import traceback
    print("Unhandled Exception:", traceback.format_exc())
    return jsonify({"success": False, "error": f"Server Error: {str(e)}"}), 500


@app.route("/")
def index():
    """Main page"""
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process_url():
    """
    YouTube URL do → transcript lo → chunks banao → embed karo → DB mein save karo.
    Agar same video pehle se DB mein hai toh directly wahan se load hoga.
    """
    # Agar data None ho toh usko khali dict `{}` maan lo
    data = request.get_json() or {}
    
    url_value = data.get("url")
    # Pylance type-narrowing ke liye isinstance check
    if not url_value or not isinstance(url_value, str):
        return jsonify({"success": False, "error": "URL dena zaroori hai aur wo string hona chahiye."}), 400

    url = url_value.strip()

    # Pehle video ID nikalo URL se (already loaded _t module se)
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({"success": False, "error": "Invalid YouTube URL. Video ID nahi mila."}), 400

    from_cache = False

    # ── Cache check: Video already DB mein hai? ──────────────────────────────
    if video_exists(video_id):
        print(f"Cache hit! '{video_id}' database mein mila.")
        transcript_data   = load_transcript(video_id)
        embedded_chunks   = load_chunks(video_id)
        from_cache        = True

    else:
        # ── Fresh fetch ──────────────────────────────────────────────────────
        print(f"'{video_id}' database mein nahi hai. YouTube se fetch kar rahe hain...")

        result = get_transcript_for_url(url)
        if not result["success"]:
            return jsonify(result), 400

        transcript_data = result["transcript"]
        language        = result.get("language", "en")

        # Chunks banao
        chunks = merge_transcript_into_chunks(transcript_data)
        if not chunks:
            return jsonify({"success": False, "error": "Chunks nahi ban sake."}), 500

        # Embeddings generate karo
        try:
            embedded_chunks = embed_chunks(chunks)
        except Exception as e:
            print(f"Embedding error: {e}")
            embedded_chunks = chunks  # Embedding fail hone par bhi aage chalo

        # ── Database mein save karo ──────────────────────────────────────────
        save_video(video_id, language)
        save_transcript(video_id, transcript_data)
        save_chunks(video_id, embedded_chunks)
        print(f"'{video_id}' database mein save ho gaya.")

    # UI ke liye formatted transcript
    formatted = format_transcript_with_timestamps(transcript_data)

    return jsonify({
        "success":      True,
        "video_id":     video_id,
        "from_cache":   from_cache,
        "total_lines":  len(formatted),
        "total_chunks": len(embedded_chunks),
        "transcript":   formatted,
    })


@app.route("/api/transcript/<video_id>", methods=["GET"])
def get_full_transcript(video_id):
    """Poora transcript database se fetch karo."""
    if not video_exists(video_id):
        return jsonify({"success": False, "error": "Transcript nahi mila. Pehle URL process karein."}), 404

    rows = load_transcript(video_id)

    formatted = [
        {
            "time":          format_time(row["start"]),
            "start_seconds": row["start"],
            "text":          row["text"],
        }
        for row in rows
    ]
    return jsonify({"success": True, "video_id": video_id, "transcript": formatted})


@app.route("/api/ask", methods=["POST"])
def ask_question():
    """
    Video ke baare mein question poocho → DB se chunks lo → AI answer dega.
    """
    data = request.get_json() or {}
    
    v_id = data.get("video_id")
    q_val = data.get("question")
    
    # Strictly check kar rahe hain ki agar string hai tabhi strip() chale
    video_id = v_id.strip() if isinstance(v_id, str) else ""
    question = q_val.strip() if isinstance(q_val, str) else ""

    if not video_id or not question:
        return jsonify({"success": False, "error": "video_id aur question dono zaroori hain."}), 400

    if not video_exists(video_id):
        return jsonify({"success": False, "error": "Pehle URL process karo."}), 400

    # Database se chunks lo
    embedded_chunks = load_chunks(video_id)

    # Relevant chunks dhundo
    try:
        relevant_chunks = find_relevant_chunks(question, embedded_chunks, top_k=4)
    except Exception as e:
        return jsonify({"success": False, "error": f"Embedding error: {str(e)}"}), 500

    if not relevant_chunks:
        return jsonify({"success": False, "error": "Relevant content nahi mila."}), 404

    # GPT ke liye context banao
    context_parts = []
    for chunk in relevant_chunks:
        start_label = format_time(chunk["start_time"])
        end_label   = format_time(chunk["end_time"])
        context_parts.append(f"[{start_label} - {end_label}] {chunk['text']}")

    context = "\n\n".join(context_parts)

    system_prompt = """Tu ek helpful YouTube video assistant hai.
Tujhe video ke transcript ke hissay diye gaye hain unke start aur end timestamps ke saath.
User ke sawal ka jawab sirf transcript ke content se de.
Answer mein exact timestamp range (jaise [02:15 - 03:00]) zaroor mention kar, jisse pata chale ki topic kahan discuss hua hai.
Agar answer transcript mein nahi hai toh seedha bol do.
Hindi aur English dono mein answer de sakta hai."""

    user_message = f"""Video Transcript ke relevant hisse:
{context}

Sawal: {question}"""

    try:
        response = get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        
        # Pylance ko batane ke liye ki content None nahi hai
        ai_content = response.choices[0].message.content
        answer = ai_content.strip() if ai_content is not None else "AI ne koi jawab nahi diya."
        
    except Exception as e:
        return jsonify({"success": False, "error": f"OpenAI error: {str(e)}"}), 500

    sources = [
        {
            "time":          f"{format_time(chunk['start_time'])} - {format_time(chunk['end_time'])}",
            "start_seconds": chunk["start_time"],
            "text":          chunk["text"][:100] + "...",
            "score":         chunk["score"],
        }
        for chunk in relevant_chunks
    ]

    return jsonify({
        "success":    True,
        "answer":     answer,
        "from_cache": True,   # Chunks hamesha DB se aate hain ab
        "sources":    sources,
    })


@app.route("/api/status/<video_id>", methods=["GET"])
def video_status(video_id):
    """Video ka status check karo database mein."""
    if not video_exists(video_id):
        return jsonify({"exists": False})

    transcript    = load_transcript(video_id)
    chunks        = load_chunks(video_id)
    has_embeddings = chunks_have_embeddings(video_id)

    return jsonify({
        "exists":           True,
        "video_id":         video_id,
        "transcript_lines": len(transcript),
        "chunks":           len(chunks),
        "embedded":         has_embeddings,
    })


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
