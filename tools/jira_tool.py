import requests
import os

JIRA_BASE = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def fetch_jira_ticket(ticket_id: str):
    url = f"{JIRA_BASE}/rest/api/3/issue/{ticket_id}"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)

    response = requests.get(url, auth=auth)
    response.raise_for_status()

    data = response.json()
    return {
        "title": data["fields"]["summary"],
        "description": data["fields"]["description"]
    }