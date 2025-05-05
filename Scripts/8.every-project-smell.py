import csv
import os
from collections import defaultdict

def load_project_names(projects_csv):
    project_names = []
    with open(projects_csv, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            if row:
                # Split "owner/repo" to get repo
                full_name = row[0].strip()
                if '/' in full_name:
                    repo = full_name.split('/')[1]
                    project_names.append((full_name, repo))
    return project_names

def sum_smells_for_project(repo_filename, smell_columns):
    smell_sums = {col: 0 for col in smell_columns}
    try:
        with open(repo_filename, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for col in smell_columns:
                    if col in row:
                        try:
                            smell_sums[col] += int(row[col])
                        except (ValueError, TypeError):
                            continue
    except FileNotFoundError:
        print(f"File not found: {repo_filename}")
    return smell_sums

def main():
    projects_csv = "Scripts/projects.csv"  # Contains "owner/repo"
    smell_results_folder = "csDetector-Result"
    output_file = "community_smell_summary.csv"

    smell_columns = ["OSE", "BCE", "PDE", "SV", "OS", "SD", "RS", "TF", "UI", "TC", "CommunitySmells"]
    
    # Load list of (owner/repo, repo) from input file
    projects = load_project_names(projects_csv)

    with open(output_file, mode="w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Project_name"] + smell_columns + ["Total_Smells"])

        for full_name, repo in projects:
            smell_file = os.path.join(smell_results_folder, f"{repo}_combined-result.csv")
            smell_sums = sum_smells_for_project(smell_file, smell_columns)
            total = sum(smell_sums.values())
            writer.writerow([full_name] + [smell_sums[col] for col in smell_columns] + [total])

    print(f"✅ Summary written to {output_file}")

if __name__ == "__main__":
    main()
