import os
import re
import time
import hashlib
import nltk
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)


# ═══════════════════════════════════════════════════════
#  ⚙️  CONFIG — Change this one line to switch models
# ═══════════════════════════════════════════════════════
PRIMARY_MODEL = "gemini"   # "ollama" or "gemini"
# ═══════════════════════════════════════════════════════


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
GEMINI_SAFE_BATCH  = 5
GEMINI_SAFE_SLEEP  = 4.5
GEMINI_BURST_LIMIT = 75
OLLAMA_BATCH       = 50
OLLAMA_SLEEP       = 0.1


# ─────────────────────────────────────────────
# Smart Embedding Wrapper
# ─────────────────────────────────────────────
class SmartEmbeddings:
    def __init__(self, api_key: str):
        self.api_key     = api_key
        self._gemini     = None
        self._ollama     = None
        self._use_ollama = (PRIMARY_MODEL == "ollama")
        self._init_ollama()
        self._init_gemini()
        print(f"🎯 Primary model : {self.active_model}")
        print(f"🔁 Fallback model: "
              f"{'Gemini (gemini-embedding-001)' if self._use_ollama else 'Ollama (nomic-embed-text)'}")

    def _init_ollama(self):
        if self._ollama is None:
            try:
                self._ollama = OllamaEmbeddings(model='nomic-embed-text:latest')
                print("✅ Ollama (nomic-embed-text) initialized.")
            except Exception as e:
                print(f"⚠️  Ollama init failed: {e}")
                self._ollama = None

    def _init_gemini(self):
        if self._gemini is None:
            try:
                self._gemini = GoogleGenerativeAIEmbeddings(
                    model="models/gemini-embedding-001",
                    google_api_key=self.api_key,
                    task_type="retrieval_document"
                )
                print("✅ Gemini (gemini-embedding-001) initialized.")
            except Exception as e:
                print(f"⚠️  Gemini init failed: {e}")
                self._gemini = None

    def _fallback_to_ollama(self, reason: str):
        print(f"\n⚠️  Gemini failed: {reason}")
        print("🔄 Falling back to Ollama...\n")
        self._use_ollama = True
        if self._ollama is None:
            self._init_ollama()
        if self._ollama is None:
            raise RuntimeError("❌ Both Gemini and Ollama are unavailable.")

    def _fallback_to_gemini(self, reason: str):
        print(f"\n⚠️  Ollama failed: {reason}")
        print("🔄 Falling back to Gemini...\n")
        self._use_ollama = False
        if self._gemini is None:
            self._init_gemini()
        if self._gemini is None:
            raise RuntimeError("❌ Both Ollama and Gemini are unavailable.")

    def switch_to_ollama(self, reason: str):
        self._fallback_to_ollama(reason)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self._use_ollama:
            if self._ollama is None:
                self._init_ollama()
            try:
                return self._ollama.embed_documents(texts)
            except Exception as e:
                self._fallback_to_gemini(str(e))
                return self._gemini.embed_documents(texts)
        else:
            if self._gemini is None:
                self._init_gemini()
            try:
                return self._gemini.embed_documents(texts)
            except Exception as e:
                self._fallback_to_ollama(str(e))
                return self._ollama.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        if self._use_ollama:
            if self._ollama is None:
                self._init_ollama()
            try:
                return self._ollama.embed_query(text)
            except Exception as e:
                self._fallback_to_gemini(str(e))
        try:
            return GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=self.api_key,
                task_type="retrieval_query"
            ).embed_query(text)
        except Exception as e:
            self._fallback_to_ollama(str(e))
            return self._ollama.embed_query(text)

    @property
    def active_model(self) -> str:
        return "Ollama (nomic-embed-text)" if self._use_ollama else "Gemini (gemini-embedding-001)"


# ─────────────────────────────────────────────
# Adaptive Batch Strategy
# ─────────────────────────────────────────────
class BatchStrategy:
    def __init__(self, total_chunks: int, use_ollama: bool):
        self.total_chunks = total_chunks
        self.use_ollama   = use_ollama
        self._compute()

    def _compute(self):
        if self.use_ollama:
            self.batch_size = OLLAMA_BATCH
            self.sleep_time = OLLAMA_SLEEP
            self.mode       = "fast"
        elif self.total_chunks <= GEMINI_BURST_LIMIT:
            self.batch_size = GEMINI_SAFE_BATCH
            self.sleep_time = 0
            self.mode       = "burst"
        else:
            self.batch_size = GEMINI_SAFE_BATCH
            self.sleep_time = GEMINI_SAFE_SLEEP
            self.mode       = "paced"
        self._log()

    def _log(self):
        total_batches = -(-self.total_chunks // self.batch_size)
        est_seconds   = total_batches * self.sleep_time
        print(f"📊 Batch Strategy : [{self.mode.upper()}]")
        print(f"   Chunks         : {self.total_chunks}")
        print(f"   Batch size     : {self.batch_size}")
        print(f"   Total batches  : {total_batches}")
        print(f"   Sleep/batch    : {self.sleep_time}s")
        if est_seconds < 5:
            print(f"   Est. build time: ⚡ instant")
        elif est_seconds < 60:
            print(f"   Est. build time: ~{int(est_seconds)}s")
        else:
            print(f"   Est. build time: ~{est_seconds / 60:.1f} min")
        print()

    def update_for_ollama(self):
        self.use_ollama = True
        self.batch_size = OLLAMA_BATCH
        self.sleep_time = OLLAMA_SLEEP
        self.mode       = "fast"
        print("⚡ Strategy updated → Ollama fast mode\n")

    def update_for_gemini(self):
        self.use_ollama = False
        self.batch_size = GEMINI_SAFE_BATCH
        self.sleep_time = GEMINI_SAFE_SLEEP if self.total_chunks > GEMINI_BURST_LIMIT else 0
        self.mode       = "paced" if self.sleep_time > 0 else "burst"
        print(f"🐢 Strategy updated → Gemini {self.mode} mode\n")


# ─────────────────────────────────────────────
# Main RAG System
# ─────────────────────────────────────────────
class YouTubeRAG:
    def __init__(self, api_key: str, db_path: str = "./DATABASE"):
        self.api_key    = api_key
        self.db_path    = db_path
        self.embeddings = SmartEmbeddings(api_key)
        self.reranker   = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def _generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_chunks(self, transcript: str) -> list[str]:
        parts = re.split(r'(\*\*\[\d{1,3}:\d{2}(?::\d{2})?\]\*\*)', transcript)
        segments = []
        for i in range(1, len(parts) - 1, 2):
            timestamp, text = parts[i], parts[i + 1].strip()
            if text and "[Music]" not in text:
                segments.append(f"{timestamp} {text}")

        raw_chunks = [" ".join(segments[i:i + 3]) for i in range(0, len(segments), 3)]

        final_chunks = []
        for chunk in raw_chunks:
            if len(chunk) > 6000:
                third = len(chunk) // 3
                final_chunks.extend([
                    chunk[:third],
                    chunk[third:third * 2],
                    chunk[third * 2:]
                ])
            else:
                final_chunks.append(chunk)

        return final_chunks

    def _embed_batch(
        self,
        vector_db,
        batch: list[str],
        is_first: bool,
        db_path: str,
        strategy: BatchStrategy
    ):
        max_retries = 6
        base_delay  = 15

        for attempt in range(max_retries):
            try:
                if is_first:
                    return Chroma.from_texts(
                        texts=batch,
                        embedding=self.embeddings,
                        persist_directory=db_path
                    )
                else:
                    vector_db.add_texts(texts=batch)
                    return vector_db

            except Exception as e:
                err           = str(e).lower()
                is_rate_limit = any(k in err for k in [
                    "resource_exhausted", "429", "quota", "rate limit", "too many"
                ])

                if is_rate_limit and attempt < max_retries - 1:
                    wait = base_delay * (2 ** attempt)
                    print(f"   ⏳ Rate limit. Retrying in {wait}s "
                          f"(attempt {attempt + 1}/{max_retries - 1})...")
                    time.sleep(wait)
                    continue

                if is_rate_limit:
                    print(f"   ❌ Quota exhausted after {max_retries} retries.")
                    self.embeddings.switch_to_ollama("Quota exhausted")
                    strategy.update_for_ollama()
                else:
                    if self.embeddings._use_ollama:
                        self.embeddings._fallback_to_gemini(str(e))
                        strategy.update_for_gemini()
                    else:
                        self.embeddings._fallback_to_ollama(str(e))
                        strategy.update_for_ollama()

                if is_first:
                    return Chroma.from_texts(
                        texts=batch,
                        embedding=self.embeddings,
                        persist_directory=db_path
                    )
                else:
                    vector_db.add_texts(texts=batch)
                    return vector_db

    def _get_vector_db(self, transcript: str, chunks: list[str]):
        video_id = self._generate_hash(transcript)[:16]

        # Load existing DB — check both model variants
        for suffix in ["gemini", "ollama"]:
            path = os.path.join(self.db_path, f"{video_id}_{suffix}")
            if os.path.exists(path):
                print(f"📂 Loaded existing [{suffix}] DB for video {video_id}")
                return Chroma(
                    persist_directory=path,
                    embedding_function=self.embeddings
                )

        # Fresh build
        suffix  = "ollama" if self.embeddings._use_ollama else "gemini"
        db_path = os.path.join(self.db_path, f"{video_id}_{suffix}")
        os.makedirs(db_path, exist_ok=True)

        progress_file = os.path.join(db_path, "progress.txt")
        start_index   = 0
        if os.path.exists(progress_file):
            saved = open(progress_file).read().strip()
            if saved.isdigit():
                start_index = int(saved)
                print(f"⏩ Resuming from chunk {start_index}...")

        print(f"🔨 Building DB with {self.embeddings.active_model}\n")

        strategy  = BatchStrategy(len(chunks), self.embeddings._use_ollama)
        vector_db = None

        # ✅ Only load existing DB if resuming — OUTSIDE the loop
        if start_index > 0:
            vector_db = Chroma(
                persist_directory=db_path,
                embedding_function=self.embeddings
            )

        # ✅ Loop is always at this indentation level — never inside the if block
        for i in range(start_index, len(chunks), strategy.batch_size):
            batch    = chunks[i: i + strategy.batch_size]
            is_first = vector_db is None
            end      = min(i + strategy.batch_size, len(chunks))

            icon = "⚡" if strategy.mode in ("burst", "fast") else "🐢"
            print(f"   📦 [{i + 1}–{end} / {len(chunks)}] "
                  f"{icon} {self.embeddings.active_model}")

            vector_db = self._embed_batch(
                vector_db, batch, is_first, db_path, strategy
            )

            with open(progress_file, "w") as f:
                f.write(str(end))

            if strategy.sleep_time > 0 and end < len(chunks):
                time.sleep(strategy.sleep_time)

        # ✅ These three lines are OUTSIDE the loop
        if os.path.exists(progress_file):
            os.remove(progress_file)

        print(f"\n✅ DB ready! [{self.embeddings.active_model}] "
              f"— {len(chunks)} chunks indexed\n")
        return vector_db

    # ── Full Retrieval Pipeline ───────────────
    def retrieve(self, transcript: str, user_query: str) -> list[str]:
        if not transcript:
            return []

        chunks = self.get_chunks(transcript)
        if not chunks:
            return []

        vector_db = self._get_vector_db(transcript, chunks)

        # ✅ None guard — prevents crash if build failed
        if vector_db is None:
            print("❌ vector_db is None — embedding failed")
            return []

        semantic_docs    = vector_db.similarity_search(user_query, k=15)
        semantic_results = [doc.page_content for doc in semantic_docs]

        bm25_results = BM25Retriever(chunks).search(user_query, k=15)

        fused = self._rrf_fusion(bm25_results, semantic_results)
        return self._rerank_docs(user_query, fused)

    def _rrf_fusion(self, list1: list, list2: list, k: int = 60) -> list:
        scores = {}
        for rank, doc in enumerate(list1):
            scores[doc] = scores.get(doc, 0) + 1 / (rank + k)
        for rank, doc in enumerate(list2):
            scores[doc] = scores.get(doc, 0) + 1 / (rank + k)
        return sorted(scores, key=lambda x: scores[x], reverse=True)

    def _rerank_docs(self, query: str, docs: list) -> list:
        if not docs:
            return []
        pairs  = [[query, doc] for doc in docs]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:5]]


# ─────────────────────────────────────────────
# BM25 Retriever
# ─────────────────────────────────────────────
class BM25Retriever:
    def __init__(self, chunks: list[str]):
        self.chunks     = chunks
        self.stemmer    = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.bm25       = BM25Okapi([self._preprocess(c) for c in chunks])

    def _preprocess(self, text: str) -> list[str]:
        tokens = word_tokenize(text.lower())
        return [self.stemmer.stem(t) for t in tokens
                if t.isalnum() and t not in self.stop_words]

    def search(self, query: str, k: int = 15) -> list[str]:
        scores      = self.bm25.get_scores(self._preprocess(query))
        top_indices = scores.argsort()[::-1][:k]
        return [self.chunks[i] for i in top_indices if scores[i] > 0]