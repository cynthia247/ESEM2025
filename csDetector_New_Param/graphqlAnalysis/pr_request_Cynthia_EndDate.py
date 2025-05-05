import math
import os
import csv
import sys
import json 
import pickle
import pandas as pd

# import statsAnalysis as stats
import sentistrength
import graphqlAnalysisHelper as gql
# import centralityAnalysis as centrality
from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse
from typing import List
from datetime import date, datetime, timezone
from configuration import Configuration
import pytz





def pr_to_csv(data, file_path):
    # Check if the file exists
    file_exists = True
    try:
        with open(file_path, 'r') as file:
            csv.reader(file)
    except FileNotFoundError:
        file_exists = False

    # Open the CSV file in append mode
    with open(file_path, 'a', newline='') as file:
        # Create a CSV writer object
        csv_writer = csv.writer(file)

        # Write the data to the CSV file
        # If the file is newly created, write the header first
        if not file_exists:
            csv_writer.writerow(data.keys())

        # Write the values without header
        csv_writer.writerow(data.values())


def cursor_to_csv(data, file_path):
    # Check if the file exists
    file_exists = True
    try:
        with open(file_path, 'r') as file:
            csv.reader(file)
    except FileNotFoundError:
        file_exists = False

    # Open the CSV file in append mode
    with open(file_path, 'a', newline='') as file:
        # Create a CSV writer object
        csv_writer = csv.writer(file)

        # Write the values without header
        csv_writer.writerow(data)

    

config: Configuration
senti: sentistrength.PySentiStr
delta: relativedelta
batchDates: List[datetime]



csv_file_path = "../test.csv"
cursor_file_path = "cursor.csv"

def prRequest(
    pat: str, owner: str, name: str, delta: relativedelta, batchDates: List[datetime], startDate, endDate
):
# def prRequest(
#     pat: str, owner: str, name: str, delta: relativedelta, batchDates: List[datetime]
# ):
    # print('\nbatchDates: ', batchDates)
    if os.path.getsize('cursor.csv') == 0:
        query = buildPrRequestQuery(owner, name, None)

    else:
        with open('cursor.csv', 'r') as file:
            csv_reader = csv.reader(file)
            last_row = list(csv_reader)[-1]
            cursor = ''.join(last_row)
            

        query = buildPrRequestQuery(owner, name, cursor)

    # prepare batches
    batches = []
    batch = None
    batchStartDate = startDate
    batchEndDate = endDate

    startDate = datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S%z")
    endDate = datetime.strptime(endDate, "%Y-%m-%d %H:%M:%S%z")

    # Convert datetime objects to Unix timestamps
    startDate = int(startDate.timestamp())
    endDate = int(endDate.timestamp())
    
    # endDate = endDate.replace(tzinfo=pytz.UTC)
    # print(config)
    
    n = 1

    

    while True:
        # get page
        result = gql.runGraphqlRequest(pat, query)
        # result = gql.runGraphqlRequest(owner, name, pat)
        # Cynthia_EndDate 
        if n > int(endDate):
            break
        print("...")

        # extract nodes
        nodes = result["repository"]["pullRequests"]["nodes"]

        # add results
        for node in nodes:

            createdAt = isoparse(node["createdAt"])
            closedAt = (
                datetime.now(timezone.utc)
                if node["closedAt"] is None
                else isoparse(node["closedAt"])
            )


            # Cynthia_EndDate
            createdAt1 =  int(createdAt.timestamp())
            
            n = createdAt1

            # Cynthia_EndDate
            
            if (
                createdAt1 < int(endDate) and  createdAt1 > int(startDate)
            ):
                # print("\n\nPR entering the if condition when it is within the time period")
                # print('createdAt1 : ', createdAt)
                # print('batch start date: ', batchStartDate)
                # print('batch end date: ', batchEndDate)
                
                if batch != None:
                    batches.append(batch)

                batchStartDate = batchDates[len(batches)]
                batchEndDate = batchStartDate + delta

                batch = []

                pr = {
                    "number": node["number"],
                    "createdAt": createdAt,
                    "closedAt": closedAt,
                    "comments": list(c["bodyText"] for c in node["comments"]["nodes"]),
                    "commitCount": node["commits"]["totalCount"],
                    "participants": list(),
                }
            # print(pr)
            

            # participants
                for user in node["participants"]["nodes"]:
                    gql.addLogin(user, pr["participants"])

                batch.append(pr)
   
                file_path = 'batch_list_file.pkl'
                try:
                    with open(file_path, 'rb') as existing_file:
                        existing_list = pickle.load(existing_file)
                except (FileNotFoundError, EOFError):
                # Handle the case when the file is not found or empty
                    existing_list = []

                # Append new data to the existing list
                existing_list.extend(batch)

                # Save the updated list back to the pickle file
                with open(file_path, 'ab') as file:
                    pickle.dump(existing_list, file)



        # pause.minutes(1)
        # check for next page
        pageInfo = result["repository"]["pullRequests"]["pageInfo"]
        if not pageInfo["hasNextPage"]:
            break

        cursor = pageInfo["endCursor"]
        query = buildPrRequestQuery(owner, name, cursor)
        cursor_to_csv(cursor, cursor_file_path)

        # n = n+1


        

    if batch != None:
        batches.append(batch)
   
    return batches


def buildPrRequestQuery(owner: str, name: str, cursor: str):
    return """{{
        repository(owner: "{0}", name: "{1}") {{
            pullRequests(first: 50{2}) {{
                pageInfo {{
                    endCursor
                    hasNextPage
                }}
                nodes {{
                    number
                    createdAt
                    closedAt
                    participants(first: 100) {{
                        nodes {{
                            login
                        }}
                    }}
                    commits {{
                        totalCount
                    }}
                    comments(first: 100) {{
                        nodes {{
                            bodyText
                        }}
                    }}
                }}
            }}
        }}
    }}
    """.format(
        owner, name, gql.buildNextPageQuery(cursor)
    )


import sys

pat = sys.argv[1]
owner = sys.argv[2]
name = sys.argv[3]
delta = sys.argv[4]
batchDates = sys.argv[5]
startDate = sys.argv[6]
endDate = sys.argv[7]

batches = prRequest(
    pat, owner, name, delta, batchDates, startDate, endDate
    )

# batches = prRequest(
#     pat, owner, name, delta, batchDates
#     )