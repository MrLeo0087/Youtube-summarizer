# 📺 YouTube Video Summarizer & AI Assistant

An advanced AI-powered platform that transforms YouTube videos into actionable insights. Utilizing  **RAG (Retrieval-Augmented Generation)** , it allows users to generate structured summaries, detailed notes, and engage in a context-aware chat with the video content.

---

## 🚀 Features

* **Multi-Model Intelligence:** Orchestrates **Llama 4 (via Groq)** for high-speed summarization and **Gemini 2.5** for conversational reasoning and note-taking.
* **Hybrid RAG System:** Implements `BM25Retriever` for high-precision context retrieval, ensuring the chatbot answers based strictly on the video transcript.
* **Stateful Navigation:** A custom Streamlit session-managed UI allowing seamless switching between Summary, Chat, and Notes without losing data.
* **Editable Markdown:** View and refine AI-generated content in real-time with built-in markdown editors.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Orchestration:** [LangChain](https://www.langchain.com/) & [LangGraph](https://www.langchain.com/langgraph)
* **LLMs:** * **Summarization:** `meta-llama/llama-4-scout-17b` (via Groq)
  * **Assistant:** `gemini-2.5-flash-lite` (via Google)
* **Retrieval:** BM25 (Best Matching 25) for sparse vector search.

---

## 📦 Installation & Setup

### 1. Clone the repository

**Bash**

```
git clone https://github.com/MrLeo0087/Youtube-ChatBot-.git
cd youtube-summarizer-ai
```

### 2. Install Dependencies

**Bash**

```
pip install -r requirements.txt
```

### 3. API Configuration

You will need:

* **Google AI API Key:** Get it from [Google AI Studio](https://aistudio.google.com/).
* **Groq API Key:** Get it from [Groq Cloud](https://console.groq.com/).

### 4. Run the Application

**Bash**

```
streamlit run app.py
or
python -m streamlit run app.py
```

---

## 📖 Usage Guide

1. **Get Transcript:** Paste a YouTube URL in the sidebar and click "Get Transcript".
2. **Summarize:** Navigate to the **Summary** tab to see Llama's high-level overview.
3. **Chat:** Ask specific questions in the **Chat** tab. The system uses RAG to pull the most relevant parts of the transcript to answer you.
4. **Notes:** Generate structured, long-form study notes in the **Note** tab.

---

## ⚙️ Architecture Flow

1. **Extraction:** Scrapes transcript via `youtube-transcript-api`.
2. **Processing:** Text is chunked and indexed using the BM25 algorithm.
3. **Retrieval:** User queries trigger a search across transcript chunks.
4. **Augmentation:** Context is injected into the LLM prompt.
5. **Generation:** The model streams a response based on the retrieved context.
