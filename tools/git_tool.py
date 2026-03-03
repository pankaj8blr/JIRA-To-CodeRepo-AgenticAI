import git
import os

def apply_patch_and_commit(repo_path, file_path, new_content, branch_name):
    repo = git.Repo(repo_path)

    if branch_name not in repo.heads:
        repo.git.checkout("-b", branch_name)
    else:
        repo.git.checkout(branch_name)

    full_path = os.path.join(repo_path, file_path)

    with open(full_path, "w") as f:
        f.write(new_content)

    repo.git.add(file_path)
    repo.index.commit(f"AI update: {file_path}")

    origin = repo.remote(name="origin")
    origin.push(branch_name)