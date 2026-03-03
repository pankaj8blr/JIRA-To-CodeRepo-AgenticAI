from workers.impact_engine import detect_and_generate_changes

def analyze_ticket(jira_text: str):
    return detect_and_generate_changes(jira_text)