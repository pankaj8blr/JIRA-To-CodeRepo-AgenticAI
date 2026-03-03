from typing import List, Dict
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from workers.dependency_graph import get_neighbors

COLLECTION = "java_repo"

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
qdrant = QdrantClient(host="qdrant", port=6333)
llm_client = OpenAI()


# -------------------------------------------------------
# STEP 1 — Semantic Search From JIRA
# -------------------------------------------------------

# def semantic_search(jira_ticket: str, top_k: int = 5):
#     query_vector = embeddings_model.embed_query(jira_ticket)

#     results = qdrant.search(
#         collection_name=COLLECTION,
#         query_vector=query_vector,
#         limit=top_k
#     )

#     return results
def semantic_search(jira_ticket: str, top_k: int = 5):
    query_vector = embeddings_model.embed_query(jira_ticket)

    response = qdrant.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k
    )

    return response.points


# -------------------------------------------------------
# STEP 2 — Expand Impact Using Dependency Graph
# -------------------------------------------------------

def expand_with_graph(results):
    impacted = {}

    for r in results:
        # payload = r.payload
        payload = r.payload
        score = r.score

        file_path = payload.get("file")
        method_signature = payload.get("method_signature")

        if not file_path or not method_signature:
            continue

        if file_path not in impacted:
            impacted[file_path] = {
                "methods": set(),
                "score": r.score
            }

        impacted[file_path]["methods"].add(method_signature)

        # Expand graph neighbors
        neighbors = get_neighbors(method_signature)
        for n in neighbors:
            impacted[file_path]["methods"].add(n)

    return impacted


# -------------------------------------------------------
# STEP 3 — Rank Final Impacted Files
# -------------------------------------------------------

def rank_impacted(impacted: Dict):
    ranked = sorted(
        impacted.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )

    return ranked


# -------------------------------------------------------
# STEP 4 — Generate Patch Suggestions
# -------------------------------------------------------

def generate_patch(jira_ticket: str, file_path: str, methods: List[str]):
    context = f"""
JIRA Ticket:
{jira_ticket}

Impacted File:
{file_path}

Impacted Methods:
{chr(10).join(methods)}

Generate precise code changes required.
Return output in unified diff format.
"""

    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": context}]
    )

    return response.choices[0].message.content


# -------------------------------------------------------
# MAIN API FUNCTION
# -------------------------------------------------------

def detect_and_generate_changes(jira_ticket: str):
    results = semantic_search(jira_ticket)

    impacted = expand_with_graph(results)

    ranked = rank_impacted(impacted)

    final_output = []

    for file_path, data in ranked:
        patch = generate_patch(
            jira_ticket,
            file_path,
            list(data["methods"])
        )

        final_output.append({
            "file": file_path,
            "methods": list(data["methods"]),
            "patch": patch
        })

    return final_output
