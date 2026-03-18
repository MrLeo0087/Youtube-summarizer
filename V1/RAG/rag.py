import os,shutil,re
# FOR SEMANTIC_SEARCH
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# FOR BM25
import nltk 
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')
nltk.download('stopwords')
from rank_bm25 import BM25Okapi
from sentence_transformers.cross_encoder.CrossEncoder import CrossEncoder

# INITILIZATION
DB_PATH = "./DATABASE"
embedding_model = OllamaEmbeddings(model='nomic-embed-text:latest')
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')



def chunking(transcript):
    parts = re.split(r'(\*\*\[\d{2}:\d{2}\]\*\*)', transcript)
    
    segment = []
    for i in range(1,len(parts) -1,2):
        timestamp = parts[i]
        text = parts[i+1]
        if text.strip():
            if not "[Music]" in text.strip():
                segment.append(f"{timestamp} {text}")
    
    chunks = []
    for i in range(0,len(segment),3):
        chunk = " ".join(segment[i:i+3])
        if chunk.strip():
            chunks.append(chunk)

    return chunks

def semantic_search(transcript,query,chunks):
    if os.path.exists(DB_PATH):
        print("Already Dataset")
        vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)
    else:
        vector_db = Chroma.from_texts(
            texts=chunks,
            embedding=embedding_model,
            persist_directory=DB_PATH
            )
    
    retrivel = vector_db.as_retriever(search_type = 'mmr',search_kwargs={'k':15,'fetch_k':30,'lambda_mult':0.7})
    context = retrivel.invoke(query)
    return context

class BM25Retriever:
    def __init__(self,chunk):
        self.chunks = chunk
        self.stemmer = PorterStemmer()
        self.stopword = set(stopwords.words('english'))
        self.tokenized_chunks = [self.preprocess(c) for c in chunk]
        self.bm25 = BM25Okapi(self.tokenized_chunks,k1=1.5,b=0.75)

    def preprocess(self,text):
        tokens = word_tokenize(text.lower())
        tokens = [t for t in tokens if t not in self.stopword]
        tokens = [self.stemmer.stem(t) for t in tokens]
        return tokens
    
    def query(self,query,k=15):
        if not query: return []
        if not self.chunks: return []

        tokenizer_query = self.preprocess(query)
        scores = self.bm25.get_scores(tokenizer_query)
        max_score = max(scores) if max(scores) > 0 else 1
        top_indices = scores.argsort()[::-1][:k]
        result = []
        for i in top_indices:
            if i>0:
                result.append(self.chunks[i])
        return result
    
def rrf_fusion(bm25_docs, semantic_docs,k=60):
    scores = {}
    for rank, docs in enumerate(bm25_docs):
        if docs not in scores:
            scores[docs] = 0
        scores[docs] += 1/(rank+k)

    
    for rank,docs in enumerate(semantic_docs):
        docs_id = docs.page_content
        if docs_id not in scores:
            scores[docs_id] = 0
        scores[docs_id] += 1/(rank+k)

    final = sorted(scores, key=scores.get, reverse=True)
    return final

def rerank(query,docs,top_n = 3):
    from sentence_transformers import CrossEncoder
    pairs = [(query,docs) for docs in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(docs,scores),key=lambda x: x[1],reverse=True)
    return [docs for docs, score in ranked[:top_n]]

def query(transcript,chunks,query,bm25):
    sementic_docs = semantic_search(transcript,query,chunks)
    bm25_docs = bm25.query(query)
    fusion = rrf_fusion(bm25_docs,sementic_docs)
    final_chunks = rerank(query,fusion)
    return final_chunks





