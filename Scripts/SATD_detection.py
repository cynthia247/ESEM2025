import json
import csv
import os 

def json_to_csv(json_file, csv_file):
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

if __name__ == "__main__":
    root_directory="Scripts/test/"

    for dirpath, _, filenames in os.walk(root_directory):
        for file in filenames:
            if file.lower().endswith('.json'):
                json_path = os.path.join(dirpath, file)
                csv_path = os.path.join(dirpath, os.path.splitext(file)[0]+'.csv')
                json_to_csv(json_path, csv_path)