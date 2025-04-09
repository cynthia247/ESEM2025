import subprocess
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from typing import List
import pandas as pd
import os
import shutil
import stat


# directory_name = f"transformers"
# if not os.path.exists(directory_name):
#     os.makedirs(directory_name)

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Retrying command after a short delay...")
        time.sleep(10)  # Wait for 5 seconds
        # run_command(command)
        return False
# https://github.com/apache/airflow

def command_automation():
    csv_file_path = '/home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/cursor.csv'
    pkl_file_path = '/home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/cursor_issue.csv'

    # Clear the contents of the CSV file
    with open(csv_file_path, 'w') as csv_file:
        csv_file.truncate(0)  # This will clear the file content

    # Clear the contents of the PKL file
    with open(pkl_file_path, 'wb') as pkl_file:
        pkl_file.truncate(0) 


    
    df = pd.read_csv("tool_automation/non-ml.csv")

    for i, row in df.iterrows():
        owner = row['owner']
        repo_name = row['repo']

        GITHUB_REPO = owner + '/' + repo_name
        print(f"Processing {GITHUB_REPO}...")

        if os.path.exists(f'./tool_automation/{repo_name}.csv'):
            df = pd.read_csv(f'./tool_automation/{repo_name}.csv')
            column = df['Published_at']

            flag = False
            startDate = column.iloc[-1]
            startDate = datetime.strptime(startDate, '%Y-%m-%dT%H:%M:%SZ')

            for i in range(len(column)-1, -1, -1):
                
                    start_Date = column.iloc[i]
                    startDate = datetime.strptime(start_Date, '%Y-%m-%dT%H:%M:%SZ')    
                    end_Date = column.iloc[i-1]
                    endDate = datetime.strptime(end_Date, '%Y-%m-%dT%H:%M:%SZ')
                    
                    print('\nStartDate: ',startDate)
                    print('EndDate: ',endDate)

                    startDate = startDate.strftime("%Y-%m-%d")
                    endDate = endDate.strftime("%Y-%m-%d")

                    if startDate == endDate:
                        continue

                    directory_name = f"/home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/tool_automation/{repo_name}/release_{startDate}"
                    if not os.path.exists(directory_name):
                        os.makedirs(directory_name)
                        run_command(f"chmod 777 {directory_name}")


                    your_command = f'''
                    python3 /home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/csDetector.py -p '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' -r 'https://github.com/{GITHUB_REPO}' -s '/home/uji657/Downloads/Software_Maintenance_Course/Project' -o '/home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/tool_automation/{repo_name}/release_{startDate}' -sd '{startDate}' -ed '{endDate}'
                    '''
                    
                    success = run_command(your_command)
                    if not success:
                        continue
                    dict = '/home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/dict.csv'
                    df = pd.read_csv(dict)
                    output_directory = f'/home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/tool_automation/{repo_name}/release_{startDate}'
                    result = f"cs_results_{startDate}"
                    output_file_path = os.path.join(output_directory, result)
                    df.to_csv(output_file_path, index=False)

                    # # Delete the downloaded repo
                    # repository_dir = f"/home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/tool_automation/{owner}"
                    # shutil.rmtree(repository_dir)


            
    

command_automation()