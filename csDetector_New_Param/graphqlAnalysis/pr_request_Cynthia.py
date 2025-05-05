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
# import itertools
# import threading
# from collections import Counter




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
    pat: str, owner: str, name: str, delta: relativedelta, batchDates: List[datetime]
):
    
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
    batchStartDate = None
    batchEndDate = None
    n = 1
    while True:
        # get page
        result = gql.runGraphqlRequest(pat, query)
        # result = gql.runGraphqlRequest(owner, name, pat)
        
        print("...")
        # print('pr result: ', result)

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

            createdAt1 = createdAt.strftime("%d %B, %Y")
            if batchEndDate == None or (
                createdAt1 > batchEndDate and len(batches) < len(batchDates) - 1
            ):
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
            

            # participants
            for user in node["participants"]["nodes"]:
                gql.addLogin(user, pr["participants"])

            # pr_to_csv(pr, csv_file_path)
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


        

    if batch != None:
        batches.append(batch)
        
    return batches


def buildPrRequestQuery(owner: str, name: str, cursor: str):
    return """{{
        repository(owner: "{0}", name: "{1}") {{
            pullRequests(first: 10{2}) {{
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

batches = prRequest(
    pat, owner, name, delta, batchDates
    )