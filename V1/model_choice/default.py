from langchain_groq import ChatGroq
from model_choice.promt import default_note_prompt,default_rag_prompt,default_summary_prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI


summarize_model ='meta-llama/llama-4-scout-17b-16e-instruct'
chat_model = 'gemini-2.5-flash-lite'
note_model = 'gemini-2.5-flash'

def summary(api,transcript):
    llm = ChatGroq(
        groq_api_key=api,
        model=summarize_model,
        temperature=0.1,        
        max_tokens=1024,                  
        max_retries=2,          
        
    )

    
    chain = default_summary_prompt | llm | StrOutputParser()
    response = chain.invoke({'transcript':transcript})
    return response


def note(api,transcript):
    llm = ChatGoogleGenerativeAI(
        google_api_key=api,
        model=note_model, 
        temperature=0.2,           
        max_output_tokens=6000,  
        top_p=0.95,                
        top_k=40,                  
        max_retries=2      
    )        
    
    chain = default_note_prompt | llm | StrOutputParser()
    response = chain.invoke({'transcript':transcript})
    return response



    
