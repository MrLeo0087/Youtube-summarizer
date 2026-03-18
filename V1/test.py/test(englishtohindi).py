from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator
from requests import Session
import time
import random

session = Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return url

def translate_text(text, source_lang='auto'):
    try:
        return GoogleTranslator(source=source_lang, target='en').translate(text)
    except Exception as e:
        print(f"⚠️ Translation warning: {e}")
        return text

def process_transcript(transcript, should_translate=False, source_lang='auto'):
    current_block = 0
    text = ""

    for snippet in transcript:
        if hasattr(snippet, 'start'):
            seconds = snippet.start
            word = snippet.text
        else:
            seconds = snippet['start']
            word = snippet['text']

        block = int(seconds / 15)

        if block == current_block:
            text += f" {word}"
        else:
            if text.strip():
                ts_minutes = int((current_block * 15) // 60)
                ts_seconds = int((current_block * 15) % 60)
                final_text = translate_text(text.strip(), source_lang) if should_translate else text.strip()
                yield f"**[{ts_minutes:02d}:{ts_seconds:02d}]** {final_text}\n\n"
            current_block = block
            text = word

    if text.strip():
        ts_minutes = int((current_block * 15) // 60)
        ts_seconds = int((current_block * 15) % 60)
        final_text = translate_text(text.strip(), source_lang) if should_translate else text.strip()
        yield f"**[{ts_minutes:02d}:{ts_seconds:02d}]** {final_text}\n\n"

def transcript_generator(url):
    video_id = extract_video_id(url)
    time.sleep(random.uniform(2, 4))

    try:
        # Step 1: Try fetching English directly (manual or auto-generated)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB'])
            print("✅ Found native English transcript.")
            yield from process_transcript(transcript)
            return
        except Exception:
            pass

        # Step 2: List all transcripts to inspect what's available
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        available = list(transcript_list)

        if not available:
            yield "❌ Error: No transcripts available for this video."
            return

        print("Available transcripts:")
        for t in available:
            print(f"  - {t.language} ({t.language_code}) | translatable: {t.is_translatable}")

        # Step 3: Try YouTube's own auto-translation to English
        # This mimics what YouTube does in the CC settings menu
        for t in available:
            if t.is_translatable:
                try:
                    transcript = t.translate('en').fetch()
                    print(f"✅ YouTube auto-translated from: {t.language} ({t.language_code})")
                    yield from process_transcript(transcript)
                    return
                except Exception as te:
                    print(f"⚠️ YouTube translation failed for {t.language_code}: {te}")
                    continue

        # Step 4: Try fetching with language code + '-en' suffix 
        # YouTube sometimes exposes auto-translated tracks as separate language entries
        first_lang = available[0].language_code
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=[f'{first_lang}-en', 'en']
            )
            print("✅ Found auto-translated track via language suffix.")
            yield from process_transcript(transcript)
            return
        except Exception:
            pass

        # Step 5: Final fallback — deep-translator on raw transcript
        first = available[0]
        source_lang = first.language_code
        print(f"🔄 Falling back to deep-translator from: {first.language} ({source_lang})")
        transcript = first.fetch()
        yield from process_transcript(transcript, should_translate=True, source_lang=source_lang)

    except Exception as e:
        yield f"❌ Error: {str(e)}"


result = transcript_generator("https://www.youtube.com/watch?v=t9MJ1gxcJ4w")
for i in result:
    print(i, end="", flush=True)