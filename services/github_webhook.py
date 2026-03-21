from flask import Flask, request, jsonify
import hmac
import hashlib
import os

from workers.tasks import incremental_index_task

app = Flask(__name__)

GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_signature(payload, signature):
    if not GITHUB_SECRET:
        return True  # skip if not set

    mac = hmac.new(
        GITHUB_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    )

    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)


@app.route("/webhook", methods=["POST"])
def github_webhook():
    signature = request.headers.get("X-Hub-Signature-256", "")
    payload = request.data

    if not verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 403

    event = request.headers.get("X-GitHub-Event")

    if event == "push":
        data = request.json

        changed_files = set()

        for commit in data.get("commits", []):
            changed_files.update(commit.get("added", []))
            changed_files.update(commit.get("modified", []))

        java_files = [f for f in changed_files if f.endswith(".java")]

        if java_files:
            incremental_index_task.delay(java_files)

    return jsonify({"status": "received"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)