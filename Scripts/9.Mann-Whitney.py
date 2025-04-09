import csv
import os
from collections import defaultdict

def main():
    base_directory = "Project-types"

    # Smell columns of interest
    smell_columns = ["OSE", "BCE", "PDE", "SV", "OS", "SD", "RS", "TF", "UI", "TC"]

    # Dictionary to accumulate smell values per project
    project_sums = defaultdict(lambda: {col: 0 for col in smell_columns})

    # Traverse all CSV files in subdirectories
    for dirname, _, filenames in os.walk(base_directory):
        for file in filenames:
            if file.endswith('.csv'):
                csv_file_path = os.path.join(dirname, file)
                print(f"Processing {csv_file_path}...")

                with open(csv_file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        project_name = row.get("Project_names")
                        if not project_name:
                            continue
                        for col in smell_columns:
                            if col in row:
                                try:
                                    project_sums[project_name][col] += int(row[col])
                                except (ValueError, TypeError):
                                    continue  # skip invalid values

    # Write output CSV
    output_file = "project_smell_summary.csv"
    with open(output_file, mode="w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        header = ["Project_name"] + smell_columns + ["Total_Smells"]
        writer.writerow(header)

        for project, smells in project_sums.items():
            smell_values = [smells[col] for col in smell_columns]
            total = sum(smell_values)
            writer.writerow([project] + smell_values + [total])

    print(f"Summary written to {output_file}")

if __name__ == "__main__":
    main()
