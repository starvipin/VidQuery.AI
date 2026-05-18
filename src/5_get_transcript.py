"""
5_get_transcript.py
YouTube URL se transcript (CC) + timestamps fetch karo.
Updated for latest youtube-transcript-api
"""

import re
import json

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)


# ─────────────────────────────────────────────
# YouTube URL se Video ID nikalo
# ─────────────────────────────────────────────
def extract_video_id(url: str) -> str | None:
    """
    Supports:
    - youtube.com/watch?v=ID
    - youtu.be/ID
    - youtube.com/shorts/ID
    - youtube.com/embed/ID
    """

    patterns = [
        r"(?:youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


# ─────────────────────────────────────────────
# Transcript Fetch Function
# ─────────────────────────────────────────────
def fetch_transcript(
    video_id: str,
    preferred_langs: list[str] | None = None
) -> dict:
    """
    YouTube transcript fetch karo.

    Returns:
    {
        "success": True,
        "video_id": "...",
        "language": "en",
        "transcript": [...]
    }
    """

    if preferred_langs is None:
        preferred_langs = ["hi", "en", "en-IN"]

    try:
        # API instance
        ytt_api = YouTubeTranscriptApi()

        # Transcript list fetch
        transcript_list = ytt_api.list(video_id)

        transcript = None
        used_lang = None

        # Preferred language try karo
        for lang in preferred_langs:
            try:
                transcript = transcript_list.find_transcript([lang])
                used_lang = lang
                break

            except Exception:
                continue

        # Agar preferred language nahi mili
        if transcript is None:
            transcript = transcript_list.find_transcript(["en"])
            used_lang = "en"

        # Transcript data fetch
        data = transcript.fetch()

        result = []

        for item in data:
            result.append({
                "text": item.text,
                "start": item.start,
                "duration": item.duration,
            })

        return {
            "success": True,
            "video_id": video_id,
            "language": used_lang,
            "transcript": result,
        }

    except NoTranscriptFound:
        return {
            "success": False,
            "error": "Is video mein transcript available nahi hai."
        }

    except TranscriptsDisabled:
        return {
            "success": False,
            "error": "Is video mein captions disabled hain."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ─────────────────────────────────────────────
# Main URL Handler
# ─────────────────────────────────────────────
def get_transcript_for_url(url: str) -> dict:
    """
    URL do → transcript lo
    """

    # Video ID nikalo
    video_id = extract_video_id(url)

    if not video_id:
        return {
            "success": False,
            "error": "Invalid YouTube URL. Video ID nahi mila."
        }

    print(f"\n🔄 Fetching transcript for: {video_id}")

    result = fetch_transcript(video_id)

    if not result["success"]:
        return result

    print(
        f"✅ Transcript fetched successfully "
        f"({len(result['transcript'])} lines)"
    )

    result["from_cache"] = False

    return result


# ─────────────────────────────────────────────
# Timestamp Formatter
# ─────────────────────────────────────────────
def format_transcript_with_timestamps(
    transcript: list
) -> list:
    """
    Transcript ko readable timestamp format me convert karo.
    """

    formatted = []

    for item in transcript:

        seconds = int(item.get("start", 0))

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            time_str = f"{minutes:02d}:{secs:02d}"

        formatted.append({
            "time": time_str,
            "start_seconds": item.get("start", 0),
            "text": item.get("text", "").strip(),
        })

    return formatted


# ─────────────────────────────────────────────
# Save Transcript JSON
# ─────────────────────────────────────────────
def save_transcript_json(
    data: dict,
    filename: str = "transcript.json"
):
    """
    Transcript JSON file me save karo.
    """

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(f"\n💾 Saved to: {filename}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":

    test_url = input("🎥 YouTube URL dalo: ").strip()

    result = get_transcript_for_url(test_url)

    if result["success"]:

        formatted = format_transcript_with_timestamps(
            result["transcript"]
        )

        print(f"\n📺 Video ID : {result['video_id']}")
        print(f"🌐 Language : {result['language']}")
        print(f"📝 Total lines : {len(formatted)}\n")

        # First 10 lines print karo
        for item in formatted[:10]:
            print(f"[{item['time']}] {item['text']}")

        print("\n...")

        # JSON save
        save_transcript_json(result)

    else:
        print(f"\n❌ Error: {result['error']}")