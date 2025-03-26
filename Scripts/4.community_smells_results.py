import pandas as pd
import os
from datetime import datetime
import re

def extracting_community_smells():
    df = pd.read_csv('csDetector-Result/project_names.csv')
    df_final_all = pd.DataFrame()
    
    for i, row in df.iterrows():
        # if i == 1: break  # Remove this later if you want to process all projects
        project_name = row['Project_names']
        print(f"\n📁 Processing project: {project_name}")

        df_date = pd.read_csv(f'csDetector-Result/{project_name}.csv')
        output_csv = f'csDetector-Result/{project_name}_combined-result.csv'

        df_date['date'] = pd.to_datetime(df_date['published_at']).dt.date.astype(str)
        releases = df_date['Release']
        column = df_date['date']

        data_rows = []
        for idx in range(len(column)-1, -1, -1):
            start_Date = column.iloc[idx]
            release_name = releases.iloc[idx]
            text_file = f'csDetector-Result/{project_name}/release_{start_Date}/cs_results_{start_Date}'

            if os.path.exists(text_file):
                # Initialize default values
                row_data = {
                    'Project_names': project_name,
                    'Release': release_name,
                    'Date': start_Date,
                    'OSE': 0, 'BCE': 0, 'PDE': 0, 'SV': 0,
                    'OS': 0, 'SD': 0, 'RS': 0, 'TF': 0,
                    'UI': 0, 'TC': 0
                }

                with open(text_file, 'r') as file:
                    lines = file.readlines()

                smell_names = []
                for line in lines:
                    if line.startswith('Smell'):
                        match = re.search(r"'([A-Z]+)", line)
                        if match:
                            smell_code = match.group(1)
                            smell_names.append(smell_code)

                for smell in smell_names:
                    if smell in row_data:
                        row_data[smell] = 1

                data_rows.append(row_data)
            else:
                print(f"⚠️ Skipped: {text_file} not found.")

        # Create a DataFrame and append
        df_final = pd.DataFrame(data_rows)

        if not os.path.exists(output_csv):
            df_final.to_csv(output_csv, index=False)
        else:
            df_final.to_csv(output_csv, index=False)

if __name__ == '__main__':
    extracting_community_smells()
