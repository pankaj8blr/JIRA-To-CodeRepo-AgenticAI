import os
import requests
from requests.auth import HTTPBasicAuth
# from tools.jira_tool import fetch_jira_ticket
def get_ticket_context(ticket_id):
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    url = f"{base_url}/rest/api/3/issue/{ticket_id}"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"},
    )

    if response.status_code != 200:
        raise Exception(f"Failed to fetch JIRA ticket: {response.text}")

    data = response.json()

    summary = data["fields"]["summary"]
    description = data["fields"]["description"]

    # Safely extract plain text description
    desc_text = ""
    if description:
        for block in description.get("content", []):
            for item in block.get("content", []):
                desc_text += item.get("text", "")

    return f"{summary}\n\n{desc_text}"
