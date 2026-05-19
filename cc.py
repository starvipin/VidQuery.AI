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

        import os
        import tempfile

        cookies_file = None
        proxies = None
        
        youtube_cookies_env = os.getenv("YOUTUBE_COOKIES")
        if youtube_cookies_env:
            temp_dir = tempfile.gettempdir()
            cookies_file = os.path.join(temp_dir, "youtube_cookies.txt")
            with open(cookies_file, "w", encoding="utf-8") as f:
                f.write(youtube_cookies_env)
        elif os.path.exists("cookies.txt"):
            cookies_file = "cookies.txt"

        http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        if http_proxy or https_proxy:
            proxies = {}
            if http_proxy: proxies["http"] = http_proxy
            if https_proxy: proxies["https"] = https_proxy

        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=preferred_langs,
            proxies=proxies,
            cookies=cookies_file
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