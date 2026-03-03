from tools.git_tool import apply_patch_and_commit

def commit_proposed_changes(repo_path, proposals):
    branch = "ai-auto-update"

    for p in proposals:
        apply_patch_and_commit(
            repo_path,
            p["file"],
            p["patch"],
            branch
        )

    return {"status": "pushed", "branch": branch}