import json
import csv

def json_to_csv(json_file, csv_file):
    """Converts a JSON file with version keys and commit lists into a CSV file."""
    
    try:
        # Open and load the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Ensure data is a dictionary
        if not isinstance(data, dict):
            raise ValueError("JSON should be a dictionary with version keys.")

        # Open CSV file for writing
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header row
            writer.writerow(["Version", "Commit Message"])

            # Loop through each version and commit messages
            for version, commits in data.items():
                if isinstance(commits, list):
                    for commit in commits:
                        writer.writerow([version, commit])

        print(f"✅ Successfully converted {json_file} to {csv_file}")

    except Exception as e:
        print(f"❌ Error: {e}")

# Example usage
if __name__ == "__main__":
    json_file = "/home/uji657/Downloads/src/CommunitySmell-and-SATD/Scripts/commits/dowhy_commits_per_release.json"  # Replace with your JSON file
    csv_file = "/home/uji657/Downloads/src/CommunitySmell-and-SATD/Scripts/commits/dowhy_commits.csv"  # Output CSV file name
    json_to_csv(json_file, csv_file)
