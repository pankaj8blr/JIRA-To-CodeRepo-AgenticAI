import os
from celery import Celery
from workers.indexer import index_file


app = Celery("tasks",
             broker="redis://redis:6379/0",
             backend="redis://redis:6379/0")

@app.task(bind=True, autoretry_for=(Exception,),
          retry_backoff=True, max_retries=5)
def index_repo_task(self, repo_path):
    import os
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".java"):
                index_file(os.path.join(root, file))



REPO_PATH = "/app/java_repo"


@app.task
def incremental_index_task(files):
    for file in files:
        full_path = os.path.join(REPO_PATH, file)

        if os.path.exists(full_path):
            index_file(full_path)
