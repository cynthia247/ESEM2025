import json
import csv
import os 
import pandas as pd
import subprocess
import shutil

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

        


if __name__ == "__main__":
    root_directory="comments/"
    unclassified_file_directory = "mt-bert-satd-tool/unclassified_files"
    tool_directory="mt-bert-satd-tool/mt-bert-satd"
    json_to_csv(root_directory)
    copy_csv_to_SATD_detector_tool(root_directory,unclassified_file_directory)
    SATD_detection(unclassified_file_directory,tool_directory)