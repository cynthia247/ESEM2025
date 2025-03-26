import requests
import json
import pandas as pd

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

    return release_dates

# Example usage
df = pd.read_csv('csDetector-Result/project_names.csv')

for i, row in df.iterrows():
    owner = row["owner"]
    repo = row["repo"]
    token = "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"  # Replace with your GitHub token

    release_dates = get_release_dates(owner, repo, token)

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
