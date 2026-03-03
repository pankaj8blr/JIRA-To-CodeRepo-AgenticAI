from agents.jira_agent import get_ticket_context
from agents.impact_agent import analyze_ticket
from agents.proposal_agent import propose_changes
from agents.git_agent import commit_proposed_changes

REPO_PATH = "/app/java_repo"

def run_full_agentic_flow(ticket_id: str):
    
    # Step 1 – Get ticket
    # If you're  using real JIRA connector yet use this:
    # jira_text = get_ticket_context(ticket_id)

    # If you're not using real JIRA connector yet, modify orchestrator temporarily:
    jira_text = "Fix memory leak issue in observer pattern implementation"

    # Step 2 – Analyze impact
    impacted = analyze_ticket(jira_text)

    # Step 3 – Propose changes
    proposals = propose_changes(jira_text, impacted)

    # Step 4 – Commit changes
    result = commit_proposed_changes(REPO_PATH, proposals)

    return result