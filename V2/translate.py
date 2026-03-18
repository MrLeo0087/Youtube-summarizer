import time
import threading
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor, as_completed


_request_lock = threading.Lock()
_last_request_time = 0

def chunk_text(text: str, size: int = 1500) -> list:
    return [text[i:i+size] for i in range(0, len(text), size)]

def translate_chunk(index: int, chunk: str, target: str = "en", retries: int = 3) -> tuple:
    global _last_request_time

    for attempt in range(retries):
        try:
            with _request_lock:
                now = time.time()
                gap = now - _last_request_time
                if gap < 0.3:
                    time.sleep(0.3 - gap)
                _last_request_time = time.time()

            result = GoogleTranslator(source="auto", target=target).translate(chunk)
            if result and result.strip():
                print(f"  ✅ Chunk {index+1} done")
                return (index, result)
            print(f"  ⚠️ Chunk {index+1} empty on attempt {attempt+1}")

        except Exception as e:
            print(f"  ❌ Chunk {index+1} attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  

    print(f"  ⚠️ Chunk {index+1} all retries failed. Returning original.")
    return (index, chunk)


def translate_document(text: str, target: str = "en", workers: int = 4) -> str:
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)} | Workers: {workers}")
    results = [None] * len(chunks)  

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(translate_chunk, i, chunk, target): i
            for i, chunk in enumerate(chunks)
        }
        for future in as_completed(futures):
            index, translated = future.result()
            results[index] = translated  

    return " ".join(results)