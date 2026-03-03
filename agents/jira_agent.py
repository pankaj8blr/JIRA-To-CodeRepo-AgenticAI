from tools.jira_tool import fetch_jira_ticket

def get_ticket_context(ticket_id: str):
    ticket = fetch_jira_ticket(ticket_id)
    combined = f"{ticket['title']}\n{ticket['description']}"
    return combined