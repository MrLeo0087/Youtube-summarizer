from youtube_transcript_api import YouTubeTranscriptApi
from requests import Session
import time
import random

session = Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

ytt = YouTubeTranscriptApi(http_client=session)


def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return url 

def process_transcript(transcript):
    current_block = 0
    text = ""

    for snippet in transcript:
        seconds = snippet.start      
        block = int(seconds / 15)

        if block == current_block:
            text += f" {snippet.text}"  
        else:
            if text.strip():
                ts_minutes = int((current_block * 15) // 60)
                ts_seconds = int((current_block * 15) % 60)
                yield f"**[{ts_minutes:02d}:{ts_seconds:02d}]** {text.strip()}\n\n"

            current_block = block
            text = snippet.text    

    if text.strip():
        ts_minutes = int((current_block * 15) // 60)
        ts_seconds = int((current_block * 15) % 60)
        yield f"**[{ts_minutes:02d}:{ts_seconds:02d}]** {text.strip()}\n\n"


def transcript_generator(url):
    video_id = extract_video_id(url)

    time.sleep(random.uniform(4, 6))

    try:
        transcript_list = ytt.list(video_id)
    except Exception as e:
        yield f"❌ Could not access video: {e}"
        return


    available_langs = [t.language_code for t in transcript_list]

    preferred_langs = ['en', 'ar', 'fr', 'ne', 'hi'] + available_langs  # fallback to whatever exists


    try:
        transcript = transcript_list.find_generated_transcript(preferred_langs).fetch()
        yield from process_transcript(transcript)
        return

    except Exception as e:
        print(f"⚠️ Generated transcript not found: {e}")


    try:
        transcript = transcript_list.find_transcript(preferred_langs).fetch()
        print("✅ Found manual transcript")
        yield from process_transcript(transcript)
        return

    except Exception as e:
        print(f"⚠️ Manual transcript not found: {e}")

    yield "❌ Transcript not found for this video."


