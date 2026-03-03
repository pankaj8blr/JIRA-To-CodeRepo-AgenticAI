from prometheus_client import Counter, start_http_server
import time

TOKEN_COUNTER = Counter("llm_tokens_used",
                        "Total tokens consumed")

EMBED_COUNTER = Counter("embeddings_created",
                        "Number of embeddings generated")

def start_metrics():
    start_http_server(8000)

def log_tokens(count):
    TOKEN_COUNTER.inc(count)

def log_embedding():
    EMBED_COUNTER.inc()
