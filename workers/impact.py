from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient

emb = OpenAIEmbeddings(model="text-embedding-3-small")
client = QdrantClient(host="qdrant", port=6333)

jira_ticket = "Fix cache invalidation bug in UserService when session expires"

query_vector = emb.embed_query(jira_ticket)

results = client.search(
    collection_name="java_repo",
    query_vector=query_vector,
    limit=10
)

for r in results:
    print(r.payload, r.score)
