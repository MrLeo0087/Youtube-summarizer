from google import genai
from google.genai import types
import yt_dlp, os
from langsmith import traceable

def download_audio(video_url: str, output_path: str = 'audio') -> str:
    print("Downloading Audio...")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(video_url, download=True)
    return output_path + ".mp3"


def get_prompt(lang: str) -> str:
    if lang == "Nepali":
        return """तपाईं एक professional transcriptionist हुनुहुन्छ। यो audio को transcript लेख्नुहोस्।

TIMESTAMP नियम (अनिवार्य):
- हरेक line **[MM:SS]** format मा सुरु हुनुपर्छ। जस्तै: **[00:00]** **[00:15]** **[00:30]**
- हरेक 15 second मा नयाँ timestamp थप्नुहोस्
- पहिलो line **[00:00]** बाट सुरु हुनुपर्छ

भाषा नियम (अनिवार्य):
- सम्पूर्ण transcript नेपालीमा लेख्नुहोस्
- Audio मा जुनसुकै भाषामा बोलिएको भए पनि नेपालीमा अनुवाद गर्नुहोस्
- कुनै पनि English शब्द नेपालीमा अनुवाद गर्नुहोस्। जस्तै: "complete" → "पूर्ण", "easy" → "सजिलो", "programming" → "प्रोग्रामिङ"
- केवल proper nouns जस्तै: मान्छेको नाम, देशको नाम, software को नाम (Python, C++, YouTube) मात्र English मै राख्नुहोस्

OUTPUT FORMAT (यस्तै हुनुपर्छ):
**[00:00]** पहिलो 15 second को सबै कुरा यहाँ लेख्नुहोस्
**[00:15]** अर्को 15 second को सबै कुरा यहाँ लेख्नुहोस्
**[00:30]** अर्को 15 second को सबै कुरा यहाँ लेख्नुहोस्

कुनै extra comment, explanation वा introduction नलेख्नुहोस् — सिधै transcript मात्र।"""

    elif lang == "Hindi":
        return """आप एक professional transcriptionist हैं। इस audio का transcript लिखें।

TIMESTAMP नियम (अनिवार्य):
- हर line **[MM:SS]** format से शुरू होनी चाहिए। जैसे: **[00:00]** **[00:15]** **[00:30]**
- हर 15 second पर नया timestamp डालें
- पहली line **[00:00]** से शुरू होनी चाहिए

भाषा नियम (अनिवार्य):
- पूरा transcript हिंदी में लिखें
- Audio में जो भी भाषा बोली गई हो, उसे हिंदी में अनुवाद करें
- कोई भी English शब्द हिंदी में अनुवाद करें। जैसे: "complete" → "पूर्ण", "easy" → "आसान", "programming" → "प्रोग्रामिंग"
- केवल proper nouns जैसे: लोगों के नाम, देशों के नाम, software के नाम (Python, C++, YouTube) English में रखें

OUTPUT FORMAT (बिल्कुल ऐसा होना चाहिए):
**[00:00]** पहले 15 second की सारी बात यहाँ लिखें
**[00:15]** अगले 15 second की सारी बात यहाँ लिखें
**[00:30]** अगले 15 second की सारी बात यहाँ लिखें

कोई extra comment, explanation या introduction मत लिखें — सीधा transcript ही लिखें।"""

    else:
        return """You are a professional transcriptionist. Transcribe this audio.

TIMESTAMP rules (mandatory):
- Every line must start with **[MM:SS]** format. Example: **[00:00]** **[00:15]** **[00:30]**
- Add a new timestamp every 15 seconds
- First line must start with **[00:00]**

Language rules (mandatory):
- Write the entire transcript in English
- Translate any non-English spoken words into English
- Only keep proper nouns as-is: people's names, country names, software names (Python, C++, YouTube)

OUTPUT FORMAT (must look exactly like this):
**[00:00]** all speech from first 15 seconds goes here
**[00:15]** all speech from next 15 seconds goes here
**[00:30]** all speech from next 15 seconds goes here

Do not write any extra comments, explanations or introduction — just the transcript."""
@traceable(name="llm transcript generator")
def llm_transcript_generator(audio: str, api: str, lang: str = 'English'):
    print("Fetching Transcript...")
    client = genai.Client(api_key=api)
    with open(audio, 'rb') as f:
        audio_data = f.read()

    prompt = get_prompt(lang)
    buffer = ""
    full_text = ""

    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash",
        # model="gemini-3.1-flash-lite-preview",
        contents=[
            types.Part.from_bytes(
                data=audio_data,
                mime_type='audio/mp3'
            ),
            prompt
        ]
    ):
        if chunk.text:
            buffer += chunk.text
            full_text += chunk.text

            # yield complete lines as soon as they are ready
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    yield line + "\n"

    # yield any remaining content in buffer
    if buffer.strip():
        full_text_remaining = buffer
        yield buffer + "\n"

    # save full transcript to file
    # with open("transcript.txt", "w", encoding="utf-8") as f:
    #     f.write(full_text)
    # print("\nTranscript saved to: transcript.txt")


def llm_transcript(youtube_url: str, api: str, lang: str):
    audio_file = None

    try:
        print("\nStep 1: Downloading audio...")
        audio_file = download_audio(youtube_url)

        print("\nStep 2: Transcribing with Gemini...\n")

        for line in llm_transcript_generator(audio_file, api, lang):
            yield line

    finally:
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
            print("\nCleaned up audio file.")


# # ─── RUN ──────────────────────────────────────────────────
# if __name__ == "__main__":
#     url = "https://www.youtube.com/watch?v=j8nAHeVKL08&list=PLu0W_9lII9agpFUAlPFe_VNSlXW5uE0YL"
#     api = "AIzaSyBphAo-Mh4IowdgQopMfWHb228fdhhBkpw"
#     lang = "Nepali"

#     transcript = llm_transcript(url, api, lang)

#     print("\n--- TRANSCRIPT ---")
#     for i in transcript:
#         print(i, end="", flush=True)