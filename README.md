# 📹 YouTube Video Intelligence Tool

> **L**earn · **I**ntelligence · **G**enerate · **H**elp · **T**ranscribe

A powerful AI-powered YouTube video processing tool that turns any YouTube video into transcripts, structured notes, smart summaries, and an interactive chat experience — all in your language of choice.

---

## 🌟 What Is This?

This is a Streamlit-based web application that lets you extract maximum value from YouTube videos without watching them fully. Whether you're a student, researcher, content creator, or just someone who wants to learn faster —This gives you everything you need from a video in minutes.

Paste a YouTube link. Get a transcript, a summary, detailed notes, and even a chatbot to talk about the video — all in  **English, Hindi, or Nepali** .

---

## 🎯 Purpose

* **Save time** — get the full gist of a long video in seconds
* **Language barrier removal** — consume content in your native language
* **Deep learning** — generate structured notes like a student taking class notes
* **Interactive understanding** — ask questions about what the video said
* **Research tool** — search the web and combine it with video knowledge

---

## ✨ Key Features

### 🎙️ Transcript Extraction

* Automatically fetches transcripts from YouTube's official API
* For videos  **without subtitles/transcripts** , uses **Gemini 2.5 Flash** to transcribe directly from audio
* Supports output in **English, Hindi, and Nepali**

### 📝 Smart Summary

* Generates concise, readable summaries of any video
* Choose complexity level: **Easy / Medium / Hard**
* Choose output language: **English / Hindi / Nepali**
* Download summary as a Markdown file

### 📒 Detailed Note Generation

* Creates beautiful, structured, in-depth notes — like a student's perfect class notes
* Complexity levels: **Easy / Medium / Hard**
* Language support: **English / Hindi / Nepali**
* Downloadable as Markdown

### 💬 Chat (3 Modes)

| Mode            | Description                                               |
| --------------- | --------------------------------------------------------- |
| 🎥 Video Chat   | RAG-based chatbot — ask anything about the video content |
| 🔍 Search Chat  | Real-time web search using DDGS for current information   |
| 🤖 General Chat | Direct AI conversation, no context needed                 |

### 🌐 Multilingual Output

All features (transcript, summary, notes, chat) support output in:

* 🇬🇧 English
* 🇮🇳 Hindi
* 🇳🇵 Nepali

Translation powered by  **Deep Translate** .

---

## 🛠️ Tech Stack

| Component                 | Technology                                                   |
| ------------------------- | ------------------------------------------------------------ |
| Frontend/UI               | Streamlit                                                    |
| Transcript (YouTube)      | YouTube Transcript API                                       |
| Transcript (No subtitles) | Gemini 2.5 Flash (audio → text)                             |
| Summary Generation        | Gemini 2.5 Flash Lite                                        |
| Note Generation           | Gemini 2.5 Flash                                             |
| Chat (All modes)          | Gemini 3.1 Flash Lite (models/gemini-3.1-flash-lite-preview) |
| RAG Chat                  | Custom RAG pipeline                                          |
| Search Chat               | DuckDuckGo Search (DDGS)                                     |
| Translation               | Deep Translate                                               |
| Video Player              | streamlit-player                                             |

---

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* A [Gemini API Key](https://aistudio.google.com/api-keys) (free tier available)

### Installation

```bash
git clone https://github.com/MrLeo0087/Youtube-summarizer.git
pip install -r requirements.txt
streamlit run app.py
```

### Usage

1. Open the app in your browser
2. Paste a YouTube video URL in the sidebar
3. Enter your Gemini API key on the Home page
4. Choose your output language
5. Click **Get Transcript** (or **Get Transcript from Gemini** for videos without subtitles)
6. Navigate to  **Summary** ,  **Note** , or **Chat** from the sidebar

---

## 📁 Project Structure

```
LIGHT/
├── app.py                        # Main Streamlit application
├── summary_generator.py          # Summary generation logic
├── note_generate.py              # Note generation logic
├── translate.py                  # Translation utility (Deep Translate)
├── TRANSCRIPT/
│   ├── transcript.py             # YouTube API transcript fetcher
│   └── llm_transcript_generate.py  # Gemini audio-based transcript
├── CHAT/
│   ├── general.py                # General chat assistant
│   ├── rag_chatbot.py            # Video RAG chatbot
│   └── website_search.py        # Web search chatbot (DDGS)
└── requirements.txt
```

---

## 📌 Use Cases

* 📚 **Students** — Generate notes from lecture videos automatically
* 🔬 **Researchers** — Quickly extract key insights from conference talks
* 🌍 **Non-English speakers** — Understand English YouTube content in Nepali or Hindi
* 💼 **Professionals** — Summarize webinars and training videos
* 🎙️ **Content creators** — Get transcripts and notes from your own videos

---

## ⚠️ Limitations

* Requires a valid Gemini API key (free tier has rate limits)
* LLM-based transcript may be slow for longer videos
* Translation quality may vary for complex technical content
* DDGS search is rate-limited under heavy usage

---

## 👨‍💻 Author

**Darshan** — Built with curiosity and a lot of ☕

> *"Why watch a 2-hour video when you can understand it in 2 minutes?"*

---

## 📜 License

MIT License — feel free to use, modify, and build upon this project.
