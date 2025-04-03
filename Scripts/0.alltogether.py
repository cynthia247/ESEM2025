import pandas as pd
import requests
import json
import tqdm
import os
import re
import git
import csv
import subprocess
import shutil

def get_release_dates(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    release_dates = []
    page = 1

    while True:
        response = requests.get(url, headers=headers, params={"per_page": 100, "page": page})

        if response.status_code == 200:
            releases = response.json()
            
            if not releases:  # Stop when no more releases
                break

            release_dates.extend([(release['tag_name'], release['published_at']) for release in releases])
            page += 1  # Move to next page
        
        else:
            print(f"Failed to fetch releases: {response.status_code} - {response.text}")
            break

    if release_dates:
        for name, date in release_dates:
            print(f"Release: {name}, Published at: {date}")

        # Convert to DataFrame
        df = pd.DataFrame(release_dates, columns=['Release', 'published_at'])

        # Save to CSV
        csv_filename = f'csDetector-Result/{repo}.csv'
        df.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")
    else:
        print("No releases found or failed to fetch data.")



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



def json_to_csv(root_directory):

    for dirpath, _, filenames in os.walk(root_directory):
        for file in filenames:
            if file.lower().endswith('.json'):
                json_file = os.path.join(dirpath, file)
                csv_file = os.path.join(dirpath, os.path.splitext(file)[0]+'.csv')
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        if not isinstance(data, dict):
                            raise ValueError("JSON should be a dictionary")
                        
                        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)

                            writer.writerow(["Version", "Commit Message"])

                            for version, commits in data.items():
                                if isinstance(commits, list):
                                    for commit in commits:
                                        writer.writerow([version, commit])

                            print(f"Successfully converted {json_file} to {csv_file}")

                except Exception as e:
                    print(f"Error processing {json_file}: {e}")


def copy_csv_to_SATD_detector_tool(root_directory, unclassified_file_directory):
    print("\n")
    print("############### Copying CSV to mt-bert-SATD tool ################")
    for dirpath,_,filenames in os.walk(root_directory):
        for file in filenames:
            if file.endswith('.csv'):
                print('.')
                df = pd.read_csv(os.path.join(dirpath,file))
                # print(df.head())
                df = df['Commit Message']
                df.to_csv(f'{unclassified_file_directory}/{file}',index=False)


def SATD_detection(unclassified_file_directory,tool_directory):
    print("\n")
    print("############### Running mt-bert-SATD tool ################")

    for dirpath,_,filenames in os.walk(unclassified_file_directory):
        for file in filenames:

            output_directory = os.path.join(tool_directory, "predict_files")
            for filename in os.listdir(output_directory):
                file_path = os.path.join(output_directory, filename)
                os.remove(file_path)


            csv_file = os.path.splitext(file)[0]
            command = ["python3", "mt-bert-satd-tool/mt-bert-satd/predict.py", "--task", "4", "--data_dir", csv_file, "--output_dir", output_directory]
            print(f"Running: {' '.join(command)}")
            try:
                subprocess.run(command, check=True)
                print(f"Successfully processed {csv_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error running command for {csv_file}: {e}")
            except FileNotFoundError as e:
                print(f"Error: Could not find executable or script: {e}")
            
            shutil.copy(f'{tool_directory}/predict_files/predict_{csv_file}.csv', f'mt-bert-satd-tool/results/predict_{csv_file}.csv')



df = pd.read_csv('csDetector-Result/project_names.csv')
print(df)
for i, row in df.iterrows():
    owner = row["owner"]
    repo = row["repo"]
    token = "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"  # Replace with your GitHub token
    GITHUB_REPO = owner + '/' + repo


    get_release_dates(owner, repo, token)
    extract_comments(GITHUB_REPO,repo)
    matching_releases(repo)

    root_directory="comments/"
    unclassified_file_directory = "mt-bert-satd-tool/unclassified_files"
    tool_directory="mt-bert-satd-tool/mt-bert-satd"
    json_to_csv(root_directory)
    copy_csv_to_SATD_detector_tool(root_directory,unclassified_file_directory)
    SATD_detection(unclassified_file_directory,tool_directory)
    
        