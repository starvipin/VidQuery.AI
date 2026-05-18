"""
YouTube video se CC (Closed Captions) nikal kar TXT file me save karna
"""

import re

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)


def extract_video_id(url):
    """
    YouTube URL se video ID extract karta hai
    """

    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"

    match = re.search(pattern, url)

    if match:
        return match.group(1)

    return None


def get_transcript(video_url, preferred_langs=None):
    """
    Transcript fetch karta hai
    """

    if preferred_langs is None:
        preferred_langs = ["en", "hi"]

    video_id = extract_video_id(video_url)

    if not video_id:
        print("❌ Invalid YouTube URL")
        return None

    try:
        print("🔄 Transcript fetch ho raha hai...")

        # NEW VERSION
        ytt_api = YouTubeTranscriptApi()

        transcript = ytt_api.fetch(
            video_id,
            languages=preferred_langs
        )

        return transcript

    except NoTranscriptFound:
        print("❌ Is video me transcript available nahi hai")
        return None

    except TranscriptsDisabled:
        print("❌ Is video me captions disabled hain")
        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def save_transcript_to_txt(transcript, filename="youtube_cc.txt"):
    """
    Transcript ko txt me save karta hai
    """

    with open(filename, "w", encoding="utf-8") as file:

        for item in transcript:
            text = item.text

            # newline remove
            text = text.replace("\n", " ")

            file.write(text + "\n")

    print(f"✅ Transcript save ho gaya: {filename}")


if __name__ == "__main__":

    youtube_url = input("🎥 YouTube Video URL dalo: ")

    transcript = get_transcript(youtube_url)

    if transcript:
        save_transcript_to_txt(transcript)