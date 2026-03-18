from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import trim_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser


# trimmer = trim_messages(
#     max_tokens=50,
#     token_counter=len,
#     strategy='last',
#     start_on='human',
#     include_system=True
# )




class GeneralAssistant:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model='gemini-3.1-flash-lite-preview',
            api_key=api_key,
            temperature=0.3,
            streaming=True
        )
        
        self.prompt =ChatPromptTemplate([
    ('system',"""You are a personal ai assistance which main aim is help user in their education by giving then some knowledge about
    user query. be humble but direct
     
    RULES:
     - give short but accurate answer
     - control answer complexity according to user query
     - in some fact base question always tell user to cross check fact otherwise no need to say that
     - Try to give best answer for user query 
     
     """),
     MessagesPlaceholder(variable_name='chat_history'),
     ('human','{query}')
])
        
        # self.trimmer = trim_messages(
        #     max_tokens=50,
        #     token_counter=len,
        #     strategy='last',
        #     start_on='human',
        #     include_system=True
        # )
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def get_response(self, query: str,history: list):
        final_history = []

        for msg in history[-40:]:
            role = msg.get('role')
            content = msg.get('content')
            
            if role in ['human', 'user']:
                final_history.append(HumanMessage(content=content))
            elif role in ['assistant', 'ai']:
                final_history.append(AIMessage(content=content))

        
        full_reply = ""
        for chunk in self.chain.stream({'query': query, "chat_history": final_history}):
            full_reply += chunk
            yield chunk



   


    
