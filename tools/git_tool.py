# import git
# import os

# def apply_patch_and_commit(repo_path, file_path, new_content, branch_name):
#     repo = git.Repo(repo_path)

#     if branch_name not in repo.heads:
#         repo.git.checkout("-b", branch_name)
#     else:
#         repo.git.checkout(branch_name)

#     full_path = os.path.join(repo_path, file_path)

#     with open(full_path, "w") as f:
#         f.write(new_content)

#     repo.git.add(file_path)
#     repo.index.commit(f"AI update: {file_path}")

#     origin = repo.remote(name="origin")
#     #origin.push(branch_name)
#     repo.git.push("origin", branch_name)

import git
import os

def apply_patch_and_commit(repo_path, file_path, new_content, branch_name):
    repo = git.Repo(repo_path)

    # Configure identity
    repo.git.config("user.email", "ai-agent@local")
    repo.git.config("user.name", "AI-Agent")

    # Checkout or create branch
    if branch_name not in repo.heads:
        repo.git.checkout("-b", branch_name)
    else:
        repo.git.checkout(branch_name)

    # Write updated content
    full_path = os.path.join(repo_path, file_path)
    with open(full_path, "w") as f:
        f.write(new_content)

    repo.git.add(file_path)
    repo.index.commit(f"AI update: {file_path}")

    # Inject token into remote URL dynamically
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")

    remote_url = f"https://{username}:{token}@github.com/{username}/java-design-patterns.git"

    repo.git.remote("set-url", "origin", remote_url)

    repo.git.push("origin", branch_name)