import os
import hashlib
import logging
from typing import List

from tree_sitter import Parser
from tree_sitter_languages import get_language

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client.http import models as rest

from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from workers.dependency_graph import update_graph

# ----------------------------
# CONFIG
# ----------------------------

COLLECTION = "java_repo"
VECTOR_SIZE = 1536
BATCH_SIZE = 64
MAX_METHOD_SIZE = 5000

# ----------------------------
# LOGGING
# ----------------------------

logging.basicConfig(level=logging.INFO)

# ----------------------------
# INIT
# ----------------------------

JAVA_LANGUAGE = get_language("java")
parser = Parser()
parser.set_language(JAVA_LANGUAGE)

qdrant = QdrantClient(host="qdrant", port=6333)

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
llm_client = OpenAI()

# ----------------------------
# CACHE (in-memory)
# ----------------------------

SUMMARY_CACHE = {}
FILE_HASH_CACHE = {}

# ----------------------------
# COLLECTION SETUP
# ----------------------------

def ensure_collection():
    collections = qdrant.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION not in names:
        logging.info("Creating Qdrant collection...")
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )

# ----------------------------
# UTILITIES
# ----------------------------

def generate_id(file_path, method_signature):
    key = f"{file_path}:{method_signature}"
    return hashlib.md5(key.encode()).hexdigest()

# ----------------------------
# PARSING
# ----------------------------

def get_class_name(root_node, source_code: bytes):
    for node in root_node.children:
        if node.type == "class_declaration":
            for child in node.children:
                if child.type == "identifier":
                    return source_code[child.start_byte:child.end_byte].decode()
    return "UnknownClass"

def extract_methods(tree, source_code: bytes):
    methods = []

    cursor = tree.walk()
    stack = [cursor.node]

    while stack:
        node = stack.pop()

        if node.type == "method_declaration":
            method_code = source_code[node.start_byte:node.end_byte].decode()

            method_name = None
            for child in node.children:
                if child.type == "identifier":
                    method_name = source_code[
                        child.start_byte:child.end_byte
                    ].decode()
                    break

            methods.append({
                "method_name": method_name,
                "method_code": method_code,
            })

        for child in node.children:
            stack.append(child)

    return methods

# ----------------------------
# LLM SUMMARY (CACHED)
# ----------------------------

def summarize_method(method_code: str) -> str:

    method_hash = hashlib.md5(method_code.encode()).hexdigest()

    if method_hash in SUMMARY_CACHE:
        return SUMMARY_CACHE[method_hash]

    prompt = f"""
Summarize what this Java method does in one concise sentence.

{method_code}
"""

    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )

    summary = response.choices[0].message.content.strip()

    SUMMARY_CACHE[method_hash] = summary

    return summary

# ----------------------------
# INDEX FILE
# ----------------------------

def index_file(file_path: str, incremental=True):

    if not os.path.exists(file_path):
        logging.warning(f"File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        source_code = f.read()

    # -------- FILE CHANGE DETECTION --------
    file_hash = hashlib.md5(source_code).hexdigest()

    if FILE_HASH_CACHE.get(file_path) == file_hash:
        logging.info(f"Skipping unchanged file: {file_path}")
        return

    FILE_HASH_CACHE[file_path] = file_hash

    tree = parser.parse(source_code)

    class_name = get_class_name(tree.root_node, source_code)
    methods = extract_methods(tree, source_code)

    if not methods:
        return

    ensure_collection()

    # -------- DELETE OLD VECTORS --------
    if incremental:
        logging.info(f"Deleting old vectors for {file_path}")

        qdrant.delete(
            collection_name=COLLECTION,
            points_selector=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="file",
                        match=rest.MatchValue(value=file_path)
                    )
                ]
            )
        )

    points = []

    # -------- PROCESS METHODS --------
    for method in methods:

        method_name = method["method_name"]
        method_code = method["method_code"]

        if not method_name:
            continue

        if len(method_code) > MAX_METHOD_SIZE:
            continue

        method_signature = f"{class_name}.{method_name}"

        logging.info(f"Indexing: {method_signature}")

        try:
            summary = summarize_method(method_code)
            embedding = embeddings_model.embed_query(summary)

            point = PointStruct(
                id=generate_id(file_path, method_signature),
                vector=embedding,
                payload={
                    "file": file_path,
                    "class_name": class_name,
                    "method_name": method_name,
                    "method_signature": method_signature,
                    "code": method_code,
                    "summary": summary
                }
            )

            points.append(point)

            # Update dependency graph
            update_graph(
                file_path=file_path,
                class_name=class_name,
                method_signature=method_signature,
                method_code=method_code
            )

        except Exception as e:
            logging.error(f"Error processing {method_signature}: {e}")

    # -------- BATCH UPSERT --------
    if points:
        logging.info(f"Upserting {len(points)} vectors")

        for i in range(0, len(points), BATCH_SIZE):
            qdrant.upsert(
                collection_name=COLLECTION,
                points=points[i:i+BATCH_SIZE]
            )

# ----------------------------
# INDEX REPO
# ----------------------------

def index_repo(root_path: str):

    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith(".java"):
                full_path = os.path.join(root, file)
                index_file(full_path, incremental=False)