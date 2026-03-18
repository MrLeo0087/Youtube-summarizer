from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.rate_limiters import InMemoryRateLimiter
from model_choice.promt import default_rag_prompt 

memory = InMemorySaver()


rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.5, 
    max_bucket_size=10
)

class LightLLM(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    context: str

def chatbot_node(state: LightLLM, config):
    api_key = config["configurable"].get("api_key")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview", 
        google_api_key=api_key,
        rate_limiter=rate_limiter,
        max_retries=6,
        temperature=0.1 
    )
    
  
    inputs = {
        'context': state.get('context', 'No context provided'),
        'question': state['messages'][-1].content,
        'history': state['messages'][:-1]
    }
    
    chain = default_rag_prompt | llm
    response = chain.invoke(inputs)
    
    return {'messages': [response]}


builder = StateGraph(LightLLM)
builder.add_node('chatbot', chatbot_node)
builder.add_edge(START, 'chatbot')
builder.add_edge('chatbot', END)
app = builder.compile(checkpointer=memory)

def chat(api, query, context, thread_id='user_123'):
    config = {
        "configurable": {
            "thread_id": thread_id,
            "api_key": api
        }
    }

    input_data = {
        "messages": [HumanMessage(content=query)],
        "context": context
    }
    

    response = app.invoke(input_data, config=config)
    
    final_content = response['messages'][-1].content

    if isinstance(final_content, list):
        text_output = "".join([part['text'] for part in final_content if 'text' in part])
        return text_output

    return str(final_content)