# 🔬 Version 2 Technical Documentation

> Version 2 represents a major architectural expansion from a simple summarizer into a full-featured **video intelligence platform** with multilingual support, multi-mode chat, and dual transcript engines.

---

## 📦 What's New in V2

V1 was a basic YouTube summarizer. V2 is a complete overhaul:

| Area               | V1               | V2                                         |
| ------------------ | ---------------- | ------------------------------------------ |
| Transcript         | YouTube API only | YouTube API + Gemini audio fallback        |
| Summary            | English only     | English / Hindi / Nepali                   |
| Notes              | English only     | Full note generation (3 complexity levels) |
| Chat               | RAG Only         | 3 chat modes (RAG / Search / General)      |
| Translation        | Not available    | Deep Translate integration                 |
| Complexity control | Not available    | Easy / Medium / Hard                       |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      app.py (Streamlit)                 │
│                                                         │
│   Sidebar: URL Input + Video Preview + Navigation       │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │   Home   │  │ Summary  │  │   Note   │  │  Chat  │ │
│  │(Transcript│  │Generator │  │Generator │  │ 3-mode │ │
│  │  Engine) │  │          │  │          │  │        │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘
         │               │              │            │
    Transcript       summary_      note_          CHAT/
    /transcript.py  generator.py  generate.py  ├── general.py
    /llm_transcript               translate.py  ├── rag_chatbot.py
    _generate.py                               └── website_search.py
```

---

## 🔑 Session State Architecture

V2 uses Streamlit's `st.session_state` as its "global memory" — no database, no backend. Everything lives in session:

```python
# Core State
st.session_state.video_url        # Current video URL
st.session_state.gemini_key       # User's API key (password input, not persisted)
st.session_state.transcript       # Raw/translated transcript text
st.session_state.output_lang      # Target language for transcript

# Summary State
st.session_state.summary          # Generated summary text
st.session_state.summary_complexity  # Easy/Medium/Hard
st.session_state.summary_lang        # Language of current summary

# Note State
st.session_state.note             # Generated note text
st.session_state.note_complexity  # Easy/Medium/Hard
st.session_state.note_lang        # Language of current note

# Chat State
st.session_state.chat_page        # menu_chat / video_chat / search_chat / general_chat
st.session_state.chat_transcript  # English-translated transcript for RAG
st.session_state.rag_history      # Video chat message history
st.session_state.general_history  # General chat message history
st.session_state.search_chat_history  # Search chat message history
```

---

## 🎙️ Transcript Engine — Dual Mode

### Mode 1: YouTube API (Primary)

```
User pastes URL → transcript_generator() → YouTube Transcript API → Stream output
```

* Fast, accurate (uses official captions)
* Works only if the video has subtitles/captions

### Mode 2: Gemini Audio Transcription (Fallback)

```
User clicks "Get Transcript from Gemini" → llm_transcript() → Gemini 2.5 Flash → Stream output
```

* Slower (audio processing takes time — user warned)
* Works for **any** video, even those with no subtitles
* Uses `gemini-2.5-flash` which can process audio natively

### Post-Processing: Language Detection + Translation

After either transcript mode, the app runs language detection:

```python
# Detects Devanagari script (Hindi/Nepali)
devanagari_chars = sum(1 for c in sample if '\u0900' <= c <= '\u097F')
transcript_lang = "hi" if devanagari_chars > 20 else "en"

# Translates only if source != target language
if transcript_lang != target_lang:
    translate_document(full_transcript, target=target_lang)
```

---

## 📝 Summary Generator

**Model:** `gemini-2.5-flash-lite`

**File:** `summary_generator.py`

### Flow

```
Transcript → summary() → streaming chunks → UI display → session save
```

### Smart Regeneration Logic

The summary page has intelligent caching to avoid unnecessary API calls:

| Condition             | Action                                       |
| --------------------- | -------------------------------------------- |
| No summary exists     | Generate fresh                               |
| Complexity changed    | Regenerate (new generation needed)           |
| Language changed only | Translate existing summary (faster, cheaper) |
| Nothing changed       | Display cached summary                       |

This avoids redundant Gemini calls and saves API quota.

---

## 📒 Note Generator

**Model:** `gemini-2.5-flash`

**File:** `note_generate.py`

Uses a **more powerful model** than summary because notes need:

* Structured formatting (headers, bullet points, sub-sections)
* Higher detail and accuracy
* Better reasoning about content organization

### Complexity Levels

* **Easy** — Simple language, key points only, good for beginners
* **Medium** — Balanced detail, standard academic style
* **Hard** — Dense, technical, complete coverage of all concepts

### Known Bug (To Fix)

```python
# ❌ BUG in current code — downloads summary instead of note
st.download_button("⬇️ Download Summary", st.session_state.summary, ...)
# ✅ Should be:
st.download_button("⬇️ Download Note", st.session_state.note, ...)
```

---

## 💬 Chat System — 3 Modes

**All chat modes use:** `models/gemini-3.1-flash-lite-preview`

Chat is accessible via `st.session_state.chat_page` router:

```
chat_page = "menu_chat"     → Show mode selection menu
chat_page = "video_chat"    → RAG chatbot
chat_page = "search_chat"   → Web search chatbot
chat_page = "general_chat"  → General assistant
```

### Mode 1: Video Chat (RAG)

**File:** `CHAT/rag_chatbot.py`

**Class:** `RAGAssistant`

* Uses the video transcript as the knowledge base
* RAG = Retrieval Augmented Generation
* The transcript is always translated to **English** first before entering RAG pipeline (better embedding/retrieval quality)
* Cached with `@st.cache_resource` — RAG index built only once per session

```python
# English translation done once and stored
if not st.session_state.chat_transcript:
    final_transcript = translate_document(sample_transcript, target='en')
    st.session_state.chat_transcript = final_transcript
```

### Mode 2: Search Chat

**File:** `CHAT/website_search.py`

**Class:** `SearchAssistant`

* Uses **DDGS (DuckDuckGo Search)** for real-time web search
* Not limited to video content — can answer current events, facts, etc.
* Maintains full chat history for context

### Mode 3: General Chat

**File:** `CHAT/general.py`

**Class:** `GeneralAssistant`

* Direct LLM conversation, no video context, no web search
* Full chat history maintained across the session
* "Fun with LIGHT" — casual conversation mode

### Chat Caching Pattern

All three assistants use `@st.cache_resource`:

```python
@st.cache_resource
def get_rag(api_key):
    return RAGAssistant(api_key=api_key)
```

This ensures the assistant object (and its vector store / config) is only initialized once per session, not on every Streamlit rerun.

---

## 🌐 Translation System

**Library:** Deep Translate

**File:** `translate.py`

### Language Codes

```python
LANG_CODE = {
    "English": "en",
    "Nepali": "ne",
    "Hindi": "hi"
}
```

### Smart Skip Logic

Translation is only triggered when source and target languages differ:

```python
def translate_function(full_text, note_lang):
    # Detect script via Devanagari character count
    devanagari_chars = sum(1 for c in sample if '\u0900' <= c <= '\u097F')
    transcript_lang = "hi" if devanagari_chars > 20 else "en"
    target_lang = LANG_CODE.get(note_lang, 'en')
  
    if transcript_lang == target_lang:
        return full_text  # Skip translation
    else:
        return translate_document(full_text, target=target_lang)
```

**Limitation:** The current detection doesn't distinguish Hindi from Nepali (both Devanagari). This is a known gap.

---

## 🤖 Model Assignments Summary

| Feature            | Model                                    | Why                                            |
| ------------------ | ---------------------------------------- | ---------------------------------------------- |
| Transcript (audio) | `gemini-2.5-flash`                     | Audio understanding capability                 |
| Summary            | `gemini-2.5-flash-lite`                | Fast, cost-efficient for shorter output        |
| Notes              | `gemini-2.5-flash`                     | More powerful for structured, detailed content |
| All Chat modes     | `models/gemini-3.1-flash-lite-preview` | Low latency for conversational turns           |

---

## 🐛 Known Issues & Areas for Improvement

### Feature Wishlist for V3

* [ ] Support for non-YouTube video URLs (Vimeo, local files)
* [ ] Batch processing multiple videos
* [ ] Speaker diarization in transcripts
* [ ] Timestamp-linked transcripts (click to jump to video moment)
* [ ] User account system with saved transcripts/notes
* [ ] Export chat as PDF

---

## 📊 How to Use — Step by Step

```
1. Launch: streamlit run app.py
2. Sidebar: Paste YouTube URL
3. Home page: Enter Gemini API key + choose output language
4. Click "Get Transcript" (YouTube captions) 
   OR "Get Transcript from Gemini" (audio, for videos without subtitles)
5. Wait for transcript to stream in
6. Go to Summary → choose complexity + language → Generate
7. Go to Note → choose complexity + language → Generate
8. Go to Chat → choose mode → start chatting
```

---

## 🧠 Design Decisions & Ideas Behind V2

**Why separate Summary and Note?**

Summary = quick overview (what happened). Note = learning artifact (what to remember). Different use cases, different models, different output style.

**Why translate transcript to English for RAG?**

Embedding models and retrieval work significantly better in English. Translating to English before indexing improves chat quality dramatically, even if the user prefers Nepali or Hindi output.

**Why cache assistants with `@st.cache_resource`?**

Streamlit reruns the entire script on every interaction. Without caching, a new `RAGAssistant` (including vector store rebuild) would be created on every single message. Caching makes it fast.

**Why stream output?**

Streaming (`st.write_stream`) gives immediate visual feedback. For long notes or summaries, this makes the app feel alive and responsive rather than frozen during generation.

---

## 👨‍💻 Built By

**Darshan** — V2 | A YouTube intelligence platform that speaks your language.
