from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

VALID_LANGS       = ("English", "Nepali", "Hindi")
VALID_COMPLEXITY  = ("easy", "medium", "hard")

def get_summary_prompt(lang: str, complexity: str) -> str:

    complexity = complexity.lower()

    rules = {
        "easy":   "Use very simple language. No jargon. Short sentences. Explain any technical term immediately.",
        "medium": "Use clear language. Include technical terms with brief explanation. Balance depth and simplicity.",
        "hard":   "Use technical language. Include all formulas, code, math, algorithms, and deep concepts fully."
    }
    rules_np = {
        "easy":   "एकदम सरल भाषा। कुनै जटिल शब्द नराख्नुहोस्। प्राविधिक शब्द भएमा तुरुन्त बुझाउनुहोस्।",
        "medium": "स्पष्ट भाषा। प्राविधिक शब्द छोटो व्याख्यासहित। सरलता र गहिराइबीच सन्तुलन।",
        "hard":   "प्राविधिक भाषा। सबै formula, code, math, algorithm पूर्ण रूपमा समावेश गर्नुहोस्।"
    }
    rules_hi = {
        "easy":   "बहुत सरल भाषा। कोई जटिल शब्द नहीं। तकनीकी शब्द हो तो तुरंत समझाएं।",
        "medium": "स्पष्ट भाषा। तकनीकी शब्द संक्षिप्त व्याख्या के साथ। सरलता और गहराई का संतुलन।",
        "hard":   "तकनीकी भाषा। सभी formula, code, math, algorithm पूरी तरह शामिल करें।"
    }

    if lang == "English":
        return f"""You are an expert summarizer. Summarize this video transcript.

Complexity: {complexity.upper()} — {rules[complexity]}

Use this structure exactly:

# 📌 [Video Title]
> One-line description of what this video is about.

---

## 🧠 Core Concept
2–3 sentences on the main idea.

## 🔑 Key Points
- **Point 1** — brief explanation
- **Point 2** — brief explanation
- **Point 3** — brief explanation

## 📖 Summary
{"Detailed explanation with all technical depth, code, math, and logic." if complexity == "hard" else "Moderate explanation covering all important parts." if complexity == "medium" else "Simple explanation covering the main ideas only."}

## 💡 Takeaways
- Takeaway 1
- Takeaway 2
- Takeaway 3

{"## 🧮 Technical Details (formulas / code / math)\nInclude all technical content here." if complexity == "hard" else ""}

Output only the summary. No extra text."""

    elif lang == "Nepali":
        return f"""तपाईं एक expert summarizer हुनुहुन्छ। यो video transcript को summary बनाउनुहोस्।

जटिलता: {complexity.upper()} — {rules_np[complexity]}
भाषा: सम्पूर्ण summary नेपालीमा। Proper nouns (Python, YouTube, नाम, देश) English मै राख्नुहोस्।

यो structure ठ्याक्कै प्रयोग गर्नुहोस्:

# 📌 [Video शीर्षक]
> यो video कसबारे हो — एक लाइनमा।

---

## 🧠 मुख्य अवधारणा
मुख्य विचार २–३ वाक्यमा।

## 🔑 मुख्य बुँदाहरू
- **बुँदा १** — छोटो व्याख्या
- **बुँदा २** — छोटो व्याख्या
- **बुँदा ३** — छोटो व्याख्या

## 📖 सारांश
{"सबै प्राविधिक गहिराइ, code, math र logic सहित विस्तृत व्याख्या।" if complexity == "hard" else "सबै महत्त्वपूर्ण भागहरू समेटेर मध्यम व्याख्या।" if complexity == "medium" else "मुख्य विचारहरू मात्र सरल भाषामा।"}

## 💡 निष्कर्षहरू
- निष्कर्ष १
- निष्कर्ष २
- निष्कर्ष ३

{"## 🧮 प्राविधिक विवरण (formula / code / math)\nसबै प्राविधिक सामग्री यहाँ राख्नुहोस्।" if complexity == "hard" else ""}

केवल summary मात्र लेख्नुहोस्। अरू कुनै कुरा नलेख्नुहोस्।"""

    else:  # Hindi
        return f"""आप एक expert summarizer हैं। इस video transcript की summary बनाएं।

जटिलता: {complexity.upper()} — {rules_hi[complexity]}
भाषा: पूरी summary हिंदी में। Proper nouns (Python, YouTube, नाम, देश) English में रखें।

बिल्कुल इस structure का उपयोग करें:

# 📌 [Video शीर्षक]
> यह video किस बारे में है — एक लाइन में।

---

## 🧠 मुख्य अवधारणा
मुख्य विचार २–३ वाक्यों में।

## 🔑 मुख्य बिंदु
- **बिंदु १** — संक्षिप्त व्याख्या
- **बिंदु २** — संक्षिप्त व्याख्या
- **बिंदु ३** — संक्षिप्त व्याख्या

## 📖 सारांश
{"सभी तकनीकी गहराई, code, math और logic सहित विस्तृत व्याख्या।" if complexity == "hard" else "सभी महत्वपूर्ण हिस्सों को cover करते हुए मध्यम व्याख्या।" if complexity == "medium" else "केवल मुख्य विचार सरल भाषा में।"}

## 💡 निष्कर्ष
- निष्कर्ष १
- निष्कर्ष २
- निष्कर्ष ३

{"## 🧮 तकनीकी विवरण (formula / code / math)\nसभी तकनीकी सामग्री यहाँ रखें।" if complexity == "hard" else ""}

केवल summary लिखें। कोई extra text नहीं।"""


def summary(transcript: str, api: str, lang: str, complexity: str):

    if not api.strip():
        yield "Error: API key is missing."
        return

    if not transcript.strip():
        yield "Error: Transcript is empty."
        return

    if lang not in VALID_LANGS:
        yield f"Error: Invalid language '{lang}'. Choose from: {', '.join(VALID_LANGS)}"
        return

    complexity = complexity.lower().strip()
    if complexity not in VALID_COMPLEXITY:
        yield f"Error: Invalid complexity '{complexity}'. Choose from: {', '.join(VALID_COMPLEXITY)}"
        return
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",   
        google_api_key=api,
        temperature=0.2,
        streaming=True
    )


    prompt = ChatPromptTemplate.from_messages([
        ("system", get_summary_prompt(lang, complexity)),
        ("user",   "{transcript}")
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        for chunk in chain.stream({"transcript": transcript}):
            yield chunk
    except Exception as e:
        yield f"\nError: {str(e)}"