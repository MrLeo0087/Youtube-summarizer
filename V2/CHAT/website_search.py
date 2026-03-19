# from ddgs import DDGS
from duckduckgo_search import DDGS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
class SearchAssistant:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model='gemini-3.1-flash-lite-preview', 
            api_key=api_key,
            temperature=0.2, 
            streaming=True
        )
        
        self.prompt = ChatPromptTemplate([
            ('system', """You are LIGHT, a direct educational assistant. Your primary job is to EXTRACT answers from search results.
             
        RESULT RULES:
        1. Do not change any fact like Date, price or any fix fact
        2. You can add filler thing that does not change fact but give user more good answer
        3. Modify answer according to user ask.
             
             EXAMPLE:
             query- what is stock price of tesla 
             Action- [Do not change any fact .. just give answer from search result]

             query- what is self attention
             Action - [You can add detail from your side as well]

        OVERALL:
             You can customize answer for user and add information but not fact 

        STRICT OPERATIONAL RULES:
        1. ANSWER FIRST: Your very first sentence must be the direct answer to the user's query (e.g., "The Tesla stock price is $174.50.").
        2. NO NAVIGATIONAL FILLER: Never say "You can check this website" or "Visit this link for more info." 
        3. SOURCE AT THE END: Only provide the source URL at the very bottom of your response after the answer.
        4. DATA OVERRIDE: Use the 'Search Result' as your absolute truth. If the search result says a price or a name, state it as a fact.
        5. NO LINKS IN TEXT: Do not put hyperlinks inside your explanation. Keep them in a 'Sources' section at the end.

        STRUCTURE:
        [Direct Answer]
        [Brief Explanation/Analogy if needed for theory]
        ---
        Source: [URL]
            
        NOTE:
            Only include important and useful URL .. do not include more then 2 
        """),
            MessagesPlaceholder(variable_name='chat_history'),
            ('human','''Query: {query}\n
            Search Resut: {search_result}
            ''')
        ])


        self.side_promt = ChatPromptTemplate([
            ('system','''You are a search engine optimizer that optimize user query to get better result 
             
             RULES:
             1. Do not answer user query. just convert user query to better result in search engine
             2. Do not change the meaning and purpose of user query
             3. "If the user asks for a stock price, crypto price, or weather, append the words 'current live price' and 'market summary' to the query."

             GOOD ✔️ [Do this]
             - User query : I wanna know about man united vs aston vill match which happen recently
             - your output : Man united vs aston villa recent match result
             
             - User query : can you tell me about current stock price of tesla
             - Your output : Current stock price of tesla

             - User query : what is self attention .. explain in detail like a 5 year child
             - Your output : What is self attention


             BAD ❌[Never do this]
             - User query : i am interest on stock price of tesla
             - your output : what is current stock price of tata
            '''),
            ('human','Query : {query}')
        ])

        self.question = self.side_promt | self.llm | StrOutputParser()

        self.chain = self.prompt | self.llm | StrOutputParser()

    def _execute_search(self, query: str) -> str:
        """Universal search logic to find current (2026) data across all topics."""
        try:
            
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, region="wt-wt", max_results=5)]
            
            if not results:
                return "No search results found."
            
            return results
        
        except Exception as e:
            return f'Error: {e}'
        
    def get_response(self, query: str, history: list):
        """
        Processes the query, retrieves web context, and streams the response.
        'history' should be a list of pairs like: [[{'message': 'hi'}, {'message': 'hello'}]]
        """
        query_final = self.question.invoke({'query':query})
        web_context = self._execute_search(query_final)
    
        final_history = []
        final_history = []

        for msg in history[-10:]:
            role = msg.get('role')
            content = msg.get('content')
            
            if role in ['human', 'user']:
                final_history.append(HumanMessage(content=content))
            elif role in ['assistant', 'ai']:
                final_history.append(AIMessage(content=content))

        for chunk in self.chain.stream({
            'query': query, 
            "chat_history": final_history, 
            "search_result": web_context
        }):
            yield chunk