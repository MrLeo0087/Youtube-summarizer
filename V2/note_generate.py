import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate

VALID_LANGS = ("English", "Nepali", "Hindi")
VALID_COMPLEXITY = ("Easy", "Medium", "Hard")

def get_note_prompt(lang: str, complexity: str) -> str:
    complexity = complexity.lower()
    key = "np" if lang == "Nepali" else "hi" if lang == "Hindi" else "en"

    # Strategy: High density, zero fluff, and forced completion
    strategy = {
        "en": "Focus on the 80/20 rule: Extract the 20% of core concepts that deliver 80% of the value. Be dense, technical, and direct.",
        "np": "मुख्य २०% अवधारणाहरूमा केन्द्रित हुनुहोस्। संक्षिप्त तर पूर्ण जानकारी दिनुहोस्।",
        "hi": "80/20 नियम पर ध्यान दें। उन 20% कॉन्सेप्ट्स को पहचानें जो सबसे महत्वपूर्ण हैं।"
    }

    # Added specific instructions to manage output length for Gemini 2.5 Flash
    completion_guard = (
        "\n--- COMPLETION PROTOCOL ---\n"
        "1. MONITOR OUTPUT: If the transcript is long, prioritize density over wordiness.\n"
        "2. BUDGETING: Ensure you leave enough tokens to complete the 'Self-Assessment Quiz' and 'Visual Logic Map'.\n"
        "3. NO CUTOFFS: It is better to have a slightly shorter summary than an incomplete technical section."
    )

    if key == "en":
        instruction = (
            f"You are an Expert Technical Architect. Convert the transcript into a High-Density Study Guide.\n"
            f"STRATEGY: {strategy[key]}\n"
            f"COMPLEXITY: {complexity.upper()}.\n\n"
            "OPERATIONAL RULES:\n"
            "- NO PREAMBLE: Start directly with the H1 Title (#).\n"
            "- LATEX: Use $...$ for all mathematical variables and formulas.\n"
            "- STRUCTURE: Use H2 (##) for sections and H3 (###) for specific sub-points."
        )
        structure = (
            "# [Full Video Title]\n\n"
            "## 📌 1. Core Thesis & Context\n[One-line high-level logic]\n\n"
            "## 🧠 2. Concept Breakdown\n[Nested bullets. In HARD mode, include all code/logic here]\n\n"
            "## 🛠️ 3. Implementation & Technical Logic\n[Key formulas, pseudocode, or architectural steps]\n\n"
            "## 📝 4. Self-Assessment Quiz\n[5-10 sharp questions]\n\n"
            "## 🗺️ 5. Visual Logic Map\n```mermaid\ngraph TD\n  A[Start] --> B[Process]\n```"
        )
    
    elif key == "np":
        instruction = (
            f"तपाईं एक प्राविधिक अनुसन्धानकर्ता हुनुहुन्छ। एउटा 'CONCISE MASTER STUDY GUIDE' तयार पार्नुहोस्।\n"
            f"रणनीति: {strategy[key]}\n"
            "नियमहरू: सिधा तथ्यमा जानुहोस्, प्राविधिक शब्दहरू English मै राख्नुहोस्।"
        )
        structure = (
            "# [शीर्षक]\n\n"
            "## 📌 १. मुख्य सन्दर्भ (Context)\n\n"
            "## 🧠 २. अवधारणा विश्लेषण\n\n"
            "## 🛠️ ३. प्राविधिक कार्यान्वयन (Logic)\n\n"
            "## 📝 ४. आत्म-मूल्यांकन क्विज\n\n"
            "## 🗺️ ५. भिजुअल म्याप (Mermaid)"
        )

    else:  # Hindi
        instruction = (
            f"आप एक तकनीकी शोधकर्ता हैं। एक 'CONCISE MASTER STUDY GUIDE' तैयार करें।\n"
            f"रणनीति: {strategy[key]}\n"
            "नियम: अनावश्यक शब्दों का त्याग करें, सीधे तथ्यों को लिखें।"
        )
        structure = (
            "# [शीर्षक]\n\n"
            "## 📌 1. मुख्य संदर्भ\n\n"
            "## 🧠 2. अवधारणा विश्लेषण\n\n"
            "## 🛠️ 3. तकनीकी कार्यान्वयन\n\n"
            "## 📝 4. आत्म-मूल्यांकन क्विज\n\n"
            "## 🗺️ 5. विजुअल मैप (Mermaid)"
        )

    return instruction + completion_guard + "\n\nSTRICT STRUCTURE TO FOLLOW:\n" + structure + "\n\nTranscript: {transcript}"

def generate_note(transcript: str, api: str, lang: str, complexity: str):
    if not api.strip() or not transcript.strip():
        yield "Error: Missing API key or Transcript."
        return
    
    complexity_lower = complexity.lower()

    # Optimized for Gemini 2.5/3 Flash
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",   
        # model="models/gemini-3.1-flash-lite-preview",   
        
        google_api_key=api,
        temperature=0.2, # Lower temperature for better structural adherence
        max_output_tokens=8000 if complexity_lower == "hard" else 5000 if complexity_lower == "medium" else 3000,
        streaming=True
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=get_note_prompt(lang, complexity)),
        HumanMessagePromptTemplate.from_template(
            "TASK: Convert the following transcript into the Master Study Guide format defined above.\n"
            "Constraint: Do not exceed a medium-length response. If the transcript is long, prioritize the "
            "most important parts to ensure the response reaches the final Quiz and Mermaid diagram section "
            "before stopping. No filler text.\n\n"
            "TRANSCRIPT:\n{transcript}"
        )
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        for chunk in chain.stream({"transcript": transcript}):
            yield chunk
    except Exception as e:
        yield f"\nError: {str(e)}"