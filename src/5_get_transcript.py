import html
import json
import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import httpx
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)
from youtube_transcript_api._errors import IpBlocked, RequestBlocked
from youtube_transcript_api.proxies import GenericProxyConfig


YOUTUBE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}


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


def _proxy_urls() -> dict[str, str] | None:
    http_proxy = os.getenv("YOUTUBE_HTTP_PROXY") or os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("YOUTUBE_HTTPS_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

    if not http_proxy and not https_proxy:
        return None

    return {
        "http://": http_proxy or https_proxy,
        "https://": https_proxy or http_proxy,
    }


def _httpx_proxy_url() -> str | None:
    proxy_urls = _proxy_urls()
    if not proxy_urls:
        return None
    return proxy_urls.get("https://") or proxy_urls.get("http://")


def _with_query(url: str, extra_params: dict[str, str]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update(extra_params)
    return urlunparse(parsed._replace(query=urlencode(query)))


def _extract_json_after_marker(page_html: str, marker: str) -> dict | None:
    marker_index = page_html.find(marker)
    if marker_index == -1:
        return None

    start = page_html.find("{", marker_index)
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(page_html)):
        char = page_html[index]

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(page_html[start:index + 1])

    return None


def _pick_caption_track(caption_tracks: list[dict], preferred_langs: list[str]) -> dict | None:
    if not caption_tracks:
        return None

    for lang in preferred_langs:
        for track in caption_tracks:
            if track.get("languageCode") == lang:
                return track

    for lang in preferred_langs:
        lang_prefix = lang.split("-")[0]
        for track in caption_tracks:
            track_lang = str(track.get("languageCode", ""))
            if track_lang.split("-")[0] == lang_prefix:
                return track

    manual_tracks = [track for track in caption_tracks if track.get("kind") != "asr"]
    return manual_tracks[0] if manual_tracks else caption_tracks[0]


def _parse_caption_response(raw_text: str) -> list[dict]:
    raw_text = raw_text.strip()
    if not raw_text:
        return []

    if raw_text.startswith("{"):
        data = json.loads(raw_text)
        transcript = []
        for event in data.get("events", []):
            segments = event.get("segs") or []
            text = "".join(segment.get("utf8", "") for segment in segments).strip()
            if not text:
                continue
            transcript.append({
                "text": text,
                "start": event.get("tStartMs", 0) / 1000,
                "duration": event.get("dDurationMs", 0) / 1000,
            })
        return transcript

    root = ET.fromstring(raw_text)
    transcript = []
    for node in root.findall(".//text"):
        text = html.unescape("".join(node.itertext())).replace("\n", " ").strip()
        if not text:
            continue
        transcript.append({
            "text": text,
            "start": float(node.attrib.get("start", 0)),
            "duration": float(node.attrib.get("dur", 0)),
        })
    return transcript


def _fetch_transcript_from_watch_page(video_id: str, preferred_langs: list[str]) -> dict:
    proxy_url = _httpx_proxy_url()
    watch_url = f"https://www.youtube.com/watch?v={video_id}&hl=en"

    with httpx.Client(headers=YOUTUBE_HEADERS, follow_redirects=True, timeout=15, proxy=proxy_url) as client:
        response = client.get(watch_url)
        response.raise_for_status()

        player_response = (
            _extract_json_after_marker(response.text, "ytInitialPlayerResponse =")
            or _extract_json_after_marker(response.text, "ytInitialPlayerResponse=")
        )
        if not player_response:
            raise RuntimeError("YouTube watch page se caption metadata nahi mila.")

        caption_tracks = (
            player_response
            .get("captions", {})
            .get("playerCaptionsTracklistRenderer", {})
            .get("captionTracks", [])
        )
        track = _pick_caption_track(caption_tracks, preferred_langs)
        if not track:
            raise RuntimeError("Is video mein transcript available nahi hai.")

        caption_url = _with_query(track["baseUrl"], {"fmt": "json3"})
        caption_response = client.get(caption_url)
        caption_response.raise_for_status()

    transcript = _parse_caption_response(caption_response.text)
    if not transcript:
        raise RuntimeError("Is video mein transcript available nahi hai.")

    return {
        "success": True,
        "video_id": video_id,
        "language": track.get("languageCode", "unknown"),
        "transcript": transcript,
    }


def _fetch_transcript_from_api(video_id: str, preferred_langs: list[str]) -> dict:
    proxy_config = None
    proxy_urls = _proxy_urls()
    if proxy_urls:
        proxy_config = GenericProxyConfig(
            http_url=proxy_urls.get("http://"),
            https_url=proxy_urls.get("https://"),
        )

    ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
    transcript_list = ytt_api.list(video_id)

    transcript = None
    used_lang = None

    for lang in preferred_langs:
        try:
            transcript = transcript_list.find_transcript([lang])
            used_lang = lang
            break
        except Exception:
            continue

    if transcript is None:
        transcript = transcript_list.find_transcript(["en"])
        used_lang = "en"

    return {
        "success": True,
        "video_id": video_id,
        "language": used_lang,
        "transcript": transcript.fetch().to_raw_data(),
    }


def fetch_transcript(video_id: str, preferred_langs: list[str] | None = None) -> dict:
    """
    YouTube transcript fetch karo.
    video_id argument dena compulsory hai.
    """
    if not video_id:
        return {
            "success": False,
            "error": "fetch_transcript ko video_id nahi mili.",
        }

    if preferred_langs is None:
        preferred_langs = ["hi", "en", "en-IN"]

    try:
        return _fetch_transcript_from_api(video_id, preferred_langs)
    except NoTranscriptFound:
        try:
            return _fetch_transcript_from_watch_page(video_id, preferred_langs)
        except Exception:
            return {"success": False, "error": "Is video mein transcript available nahi hai."}
    except TranscriptsDisabled:
        return {"success": False, "error": "Is video mein captions disabled hain."}
    except (IpBlocked, RequestBlocked):
        try:
            return _fetch_transcript_from_watch_page(video_id, preferred_langs)
        except Exception:
            return {
                "success": False,
                "error": (
                    "YouTube ne deployment server ki IP block kar di hai. "
                    "Free fallback bhi block ho gaya. Paid proxy ke bina cloud par "
                    "har YouTube link guarantee ke saath fetch nahi ho sakta. "
                    "Free reliable option: app ko local machine par run karke "
                    "Cloudflare Tunnel/ngrok se public URL expose karein."
                ),
            }
    except Exception as e:
        try:
            return _fetch_transcript_from_watch_page(video_id, preferred_langs)
        except Exception:
            return {"success": False, "error": str(e)}


def get_transcript_for_url(url: str) -> dict:
    """
    Full URL handle karne ke liye.
    """
    video_id = extract_video_id(url)

    if not video_id:
        return {
            "success": False,
            "error": "Invalid YouTube URL. Video ID nahi mila.",
        }

    print(f"\nFetching transcript for Video ID: {video_id}")
    result = fetch_transcript(video_id=video_id)

    if not result["success"]:
        return result

    print(f"Transcript fetched successfully ({len(result['transcript'])} lines)")
    result["from_cache"] = False
    return result


def format_transcript_with_timestamps(transcript: list) -> list:
    """
    Timestamps formatting (HH:MM:SS)
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


def save_transcript_json(data: dict, filename: str = "transcript.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\nSaved to: {filename}")


if __name__ == "__main__":
    test_url = input("YouTube URL dalo: ").strip()

    if test_url:
        result = get_transcript_for_url(url=test_url)

        if result["success"]:
            formatted = format_transcript_with_timestamps(result["transcript"])

            print(f"\nVideo ID   : {result['video_id']}")
            print(f"Language   : {result['language']}")
            print(f"Total lines : {len(formatted)}\n")

            for item in formatted[:10]:
                print(f"[{item['time']}] {item['text']}")

            print("\n...")
            save_transcript_json(result)
        else:
            print(f"\nError: {result['error']}")
    else:
        print("\nInput khali hai. Sahi URL enter karein.")
