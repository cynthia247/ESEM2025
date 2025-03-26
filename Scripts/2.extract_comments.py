import os
import git
from tqdm import tqdm
import re
import pandas as pd
import json

# Define which file types you want to extract comments from
SOURCE_EXTENSIONS = ['.py', '.java', '.js', '.cpp', '.c']

# Simple regex patterns to capture comments
COMMENT_PATTERNS = {
        '.py': r'^\s*#(.*)',              # Python
        '.java': r'^\s*//(.*)',           # Java/C++
        '.js': r'^\s*//(.*)',             # JavaScript
        '.cpp': r'^\s*//(.*)',            # C++
        '.c': r'^\s*//(.*)'               # C
    }

# Extract comments from one file
def extract_comments_from_file(file_path):
        comments = []
        ext = os.path.splitext(file_path)[-1]
        pattern = COMMENT_PATTERNS.get(ext)
        if not pattern:
            return []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = re.match(pattern, line)
                if match:
                    comments.append(match.group(1).strip())
        return comments

# Traverse a folder and extract comments
def extract_comments_from_release(path, extensions=SOURCE_EXTENSIONS):
        all_comments = []
        for root, _, files in os.walk(path):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    comments = extract_comments_from_file(file_path)
                    all_comments.extend(comments)
        return all_comments


def extract_comments(GITHUB_REPO, repo):
    LOCAL_REPO_DIR = f"comments/{repo}"

    # Clone the repo if not already
    if not os.path.exists(LOCAL_REPO_DIR):
        print(f"📥 Cloning {repo}...")
        git.Repo.clone_from(f"https://github.com/{GITHUB_REPO}.git", LOCAL_REPO_DIR)

    repository = git.Repo(LOCAL_REPO_DIR)
    repository.git.fetch("--tags")

    # Get all tag names
    all_tags = [tag.name for tag in repository.tags]

    # Main loop over releases
    comments_by_release = {}

    for tag in tqdm(all_tags, desc="Processing releases"):
        try:
            print(f"🔁 Checking out: {tag}")
            repository.git.checkout(f"tags/{tag}")
        except Exception as e:
            print(f"⚠️ Could not checkout {tag}: {e}")
            continue

        comments = extract_comments_from_release(LOCAL_REPO_DIR)
        comments_by_release[tag] = comments

    with open(f"comments/{repo}_code_comments.json", "w", encoding="utf-8") as f:
        json.dump(comments_by_release, f, indent=2)

    print("✅ Comments extracted and saved to `code_comments_by_release.json`")


def matching_releases(repo):
    # Load release tag names from CSV
    df = pd.read_csv(f"csDetector-Result/{repo}.csv")
    csv_tags = df["Release"]  # Strip 'v' prefix if needed

    # Load JSON comments
    with open(f"comments/{repo}_code_comments.json", "r", encoding="utf-8") as f:
        all_comments = json.load(f)

    # Filter JSON by matching tags
    filtered_comments = {tag: all_comments[tag] for tag in csv_tags if tag in all_comments}

    # Save filtered JSON
    with open(f"comments/{repo}_filtered_comments.json", "w", encoding="utf-8") as f:
        json.dump(filtered_comments, f, indent=2)

    print(f"✅ Filtered {len(filtered_comments)} matched releases and saved to `filtered_comments.json`.")



if __name__ == "__main__":
    df = pd.read_csv('csDetector-Result/project_names.csv')

    for i, row in df.iterrows():
        owner = row['owner']
        repo = row['repo']
        GITHUB_REPO = owner + '/' + repo
        extract_comments(GITHUB_REPO,repo)
        matching_releases(repo)

    