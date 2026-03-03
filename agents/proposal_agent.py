from workers.impact_engine import generate_patch

def propose_changes(jira_text, impacted_files):
    proposals = []

    for file_data in impacted_files:
        patch = generate_patch(
            jira_text,
            file_data["file"],
            file_data["methods"]
        )
        proposals.append({
            "file": file_data["file"],
            "patch": patch
        })

    return proposals