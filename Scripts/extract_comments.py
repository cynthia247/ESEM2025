import re
from tqdm import tqdm
import os
import git
import json
import requests

# GitHub repository details
GITHUB_REPO = "HealthCatalyst/healthcareai-r"  # Format: "owner/repo"
LOCAL_REPO_DIR = "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"

# Clone repository if not exists
if not os.path.exists(LOCAL_REPO_DIR):
    git.Repo.clone_from(f"https://github.com/{GITHUB_REPO}.git", LOCAL_REPO_DIR)

# Get available releases from GitHub API
def get_github_releases(repo):
    url = f"https://api.github.com/repos/{repo}/releases"
    response = requests.get(url)
    if response.status_code == 200:
        return [releases["tag_name"] for releases in response.json()]
    return []

# Fetch all releases (tags)
releases = get_github_releases(GITHUB_REPO)
print("Available Releases:", releases)

# Initialize Git repository object
repo = git.Repo(LOCAL_REPO_DIR)

# Get commits per release
def get_commits_per_release(repo, releases):
    commits_per_release = {}
    for release in tqdm(releases): 
        repo.git.checkout(release)  # Switch to release
        commits_per_release[release] = [commit.message.strip() for commit in repo.iter_commits()]
    return commits_per_release

commits_per_release = get_commits_per_release(repo, releases)

print("\nCommits Per Release (All Releases):")
for release, commits in commits_per_release.items():
    print(f"\n🔹 Release: {release} - {len(commits)} commits")
    print("\n".join(commits[:5]))  # Show first 5 commits


# Save Extracted Commits for Analysis

with open("commits_per_release.json", "w", encoding="utf-8") as f:
    json.dump(commits_per_release, f, indent=4)

print("🔹 Commits saved to `commits_per_release.json`")












