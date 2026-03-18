from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import trim_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from CHAT.rag import YouTubeRAG
class RAGAssistant:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model='gemini-3.1-flash-lite-preview',
            api_key=api_key,
            temperature=0.3,
            streaming=True
        )
        
        self.prompt = ChatPromptTemplate([
        ('system', """You are a strict Educational Research Assistant. 
        Your ONLY source of information is the provided CONTEXT. 

        STRICT RULES:
        1. Answer the user query using ONLY the information found in the CONTEXT below.
        2. If the answer is not contained within the CONTEXT, explicitly state: "I'm sorry, but the provided documents do not contain information to answer this query."
        3. DO NOT use any outside knowledge, personal opinions, or external facts.
        4. Keep the answer direct, educational, and accurate to the provided text.
        5. If a fact is found in the context, do not tell the user to cross-check (since you are acting as a document-based validator).

        CONTEXT:
        {context}
        """),
        ('human', '{query}')
])
        
        self.rag = YouTubeRAG(api_key=api_key)
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def get_response(self, query: str,transcript:str):

        context = self.rag.retrieve(transcript,query)

        return self.chain.stream({
            'context': context, 
            'query': query
        })



   


    
