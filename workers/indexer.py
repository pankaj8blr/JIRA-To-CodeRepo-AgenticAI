import os
import uuid
from typing import List
import json
import tiktoken

from tree_sitter import Parser
from tree_sitter_languages import get_language
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client.http import models as rest
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from workers.dependency_graph import update_graph

COLLECTION = "java_repo"
VECTOR_SIZE = 1536


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
# Ensure Collection Exists
# ----------------------------

def ensure_collection():
    collections = qdrant.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION not in names:
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )


# ----------------------------
# Extract Class Name
# ----------------------------

def get_class_name(root_node, source_code: bytes):
    for node in root_node.children:
        if node.type == "class_declaration":
            for child in node.children:
                if child.type == "identifier":
                    return source_code[child.start_byte:child.end_byte].decode()
    return None


# ----------------------------
# Extract Methods
# ----------------------------

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
# Semantic Summary (Optional)
# ----------------------------

def summarize_method(method_code: str) -> str:
    prompt = f"""
Summarize what this Java method does in one concise sentence.

{method_code}
"""

    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )

    return response.choices[0].message.content.strip()


# ----------------------------
# Index Single File
# ----------------------------

def index_file(file_path: str):
    with open(file_path, "rb") as f:
        source_code = f.read()

    tree = parser.parse(source_code)

    class_name = get_class_name(tree.root_node, source_code)
    methods = extract_methods(tree, source_code)

    if not methods:
        return

    ensure_collection()

    points = []

    for method in methods:
        method_name = method["method_name"]
        method_code = method["method_code"]

        if not method_name:
            continue

        summary = summarize_method(method_code)

        embedding = embeddings_model.embed_query(summary)

        point = PointStruct(
            id=uuid.uuid4().int >> 64,
            vector=embedding,
            payload={
                "file": file_path,
                "class_name": class_name,
                "method_name": method_name,
                "method_signature": f"{class_name}.{method_name}",
                "code": method_code,
                "summary": summary
            }
        )

        points.append(point)

        # Update dependency graph
        update_graph(
            method_signature=f"{class_name}.{method_name}",
            method_code=method_code
        )

    if points:
        qdrant.upsert(collection_name=COLLECTION, points=points)


# ----------------------------
# Index Repo
# ----------------------------

def index_repo(root_path: str):
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith(".java"):
                full_path = os.path.join(root, file)
                print("Indexing:", full_path)
                index_file(full_path)