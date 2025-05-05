import subprocess
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from typing import List

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Retrying command after a short delay...")
        time.sleep(10)  # Wait for 5 seconds
        run_command(command)

def command_automation(pat, owner, name, delta, batchDates, batchStartDate, batchEndDate):
    
    # Replace this with your actual command
    your_command = f"python3 ./graphqlAnalysis/pr_request_Cynthia_EndDate.py '{pat}' '{owner}' '{name}' '{delta}' '{batchDates}' '{batchStartDate}' '{batchEndDate}'"
    # your_command = f"python3 ./graphqlAnalysis/pr_request_Cynthia_EndDate.py '{pat}' '{owner}' '{name}' '{delta}' '{batchDates}'"
    run_command(your_command)
