
import math
import os
import csv
import sys
from perspectiveAnalysis import getToxicityPercentage
import statsAnalysis as stats
import sentistrength
import graphqlAnalysis.graphqlAnalysisHelper as gql
import centralityAnalysis_Cynthia_EndDate as centrality
from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse
from typing import List
from datetime import date, datetime, timezone
from configuration import Configuration
import itertools
import threading
from collections import Counter
import pytz


def cursor_to_csv(data, file_path):
    file_exists = True
    try:
        with open(file_path, 'r') as file:
            csv.reader(file)
    except FileNotFoundError:
        file_exists = False

    with open(file_path, 'a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(data)

cursor_file_path = "/home/uji657/Downloads/Software_Maintenance_Course/Project/csDetector-master_NewParam/cursor.csv"

def prAnalysis(
    config: Configuration,
    senti: sentistrength.PySentiStr,
    delta: relativedelta,
    batchDates: List[datetime],
):
    if config.startDate is not None:
        startDate = datetime.strptime(config.startDate, "%Y-%m-%d")
        startDate = startDate.replace(tzinfo=pytz.UTC)
    batchStartDate = startDate

    if config.endDate is not None:
        endDate = datetime.strptime(config.endDate, "%Y-%m-%d")
        endDate = endDate.replace(tzinfo=pytz.UTC)

    batchEndDate = endDate

    print("Querying PRs")
    batches = prRequest(
        config.pat, config.repositoryOwner, config.repositoryName, delta, batchDates, batchStartDate, batchEndDate
    )

    batchParticipants = list()
    batchComments = list()

    for batchIdx, batch in enumerate(batches):
        print(f"Analyzing PR batch #{batchIdx}")

        # extract data from batch
        prCount = len(batch)
        participants = list(
            pr["participants"] for pr in batch if len(pr["participants"]) > 0
        )
        batchParticipants.append(participants)

        allComments = list()
        prPositiveComments = list()
        prNegativeComments = list()
        generallyNegative = list()

        print(f"    Sentiments per PR", end="")

        semaphore = threading.Semaphore(15)
        threads = []
        for pr in batch:

            comments = list(
                comment for comment in pr["comments"] if comment and comment.strip()
            )

            # split comments that are longer than 20KB
            splitComments = []
            for comment in comments:

                # calc number of chunks
                byteChunks = math.ceil(sys.getsizeof(comment) / (20 * 1024))
                if byteChunks > 1:

                    # calc desired max length of each chunk
                    chunkLength = math.floor(len(comment) / byteChunks)

                    # divide comment into chunks
                    chunks = [
                        comment[i * chunkLength : i * chunkLength + chunkLength]
                        for i in range(0, byteChunks)
                    ]

                    # save chunks
                    splitComments.extend(chunks)

                else:
                    # append comment as-is
                    splitComments.append(comment)

            # re-assign comments after chunking
            comments = splitComments

            if len(comments) == 0:
                prPositiveComments.append(0)
                prNegativeComments.append(0)
                continue

            allComments.extend(comments)

            thread = threading.Thread(
                target=analyzeSentiments,
                args=(
                    senti,
                    comments,
                    prPositiveComments,
                    prNegativeComments,
                    generallyNegative,
                    semaphore,
                ),
            )
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print("")

        # save comments
        batchComments.append(allComments)

        # get comment length stats
        commentLengths = [len(c) for c in allComments]

        #Cynthia_code_begins
        if prCount == 0:
            generallyNegativeRatio = 0
        #Cynthia_code_ends
        else:
            generallyNegativeRatio = len(generallyNegative) / prCount


        # get pr duration stats
        durations = [(pr["closedAt"] - pr["createdAt"]).days for pr in batch]

        print("    All sentiments")

        commentSentiments = []
        commentSentimentsPositive = 0
        commentSentimentsNegative = 0

        if len(allComments) > 0:
            commentSentiments = senti.getSentiment(allComments)
            commentSentimentsPositive = sum(
                1 for _ in filter(lambda value: value >= 1, commentSentiments)
            )
            commentSentimentsNegative = sum(
                1 for _ in filter(lambda value: value <= -1, commentSentiments)
            )

        toxicityPercentage = getToxicityPercentage(config, allComments)

        centrality.buildGraphQlNetwork(batchIdx, participants, "PRs", config)

        print("    Writing results")
        with open(
            os.path.join(config.resultsPath, f"results_{batchIdx}.csv"),
            "a",
            newline="",
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow(["NumberPRs", prCount])
            w.writerow(["NumberPRComments", len(allComments)])
            w.writerow(["PRCommentsPositive", commentSentimentsPositive])
            w.writerow(["PRCommentsNegative", commentSentimentsNegative])
            w.writerow(["PRCommentsNegativeRatio", generallyNegativeRatio])
            w.writerow(["PRCommentsToxicityPercentage", toxicityPercentage])

        with open(
            os.path.join(config.metricsPath, f"PRCommits_{batchIdx}.csv"),
            "a",
            newline="",
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow(["PR Number", "Commit Count"])
            for pr in batch:
                w.writerow([pr["number"], pr["commitCount"]])

        with open(
            os.path.join(config.metricsPath, f"PRParticipants_{batchIdx}.csv"),
            "a",
            newline="",
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow(["PR Number", "Developer Count"])
            for pr in batch:
                w.writerow([pr["number"], len(set(pr["participants"]))])

        # output statistics
        stats.outputStatistics(
            batchIdx,
            commentLengths,
            "PRCommentsLength",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            durations,
            "PRDuration",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            [len(pr["comments"]) for pr in batch],
            "PRCommentsCount",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            [pr["commitCount"] for pr in batch],
            "PRCommitsCount",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            commentSentiments,
            "PRCommentSentiments",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            [len(set(pr["participants"])) for pr in batch],
            "PRParticipantsCount",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            prPositiveComments,
            "PRCountPositiveComments",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            prNegativeComments,
            "PRCountNegativeComments",
            config.resultsPath,
        )

    return batchParticipants, batchComments


def analyzeSentiments(
    senti, comments, positiveComments, negativeComments, generallyNegative, semaphore
):
    with semaphore:
        commentSentiments = (
            senti.getSentiment(comments, score="scale")
            if len(comments) > 1
            else senti.getSentiment(comments[0])
        )

        commentSentimentsPositive = sum(
            1 for _ in filter(lambda value: value >= 1, commentSentiments)
        )
        commentSentimentsNegative = sum(
            1 for _ in filter(lambda value: value <= -1, commentSentiments)
        )

        lock = threading.Lock()
        with lock:
            positiveComments.append(commentSentimentsPositive)
            negativeComments.append(commentSentimentsNegative)

            if commentSentimentsNegative / len(comments) > 0.5:
                generallyNegative.append(True)

            print(f".", end="")


def prRequest(
    pat: str, owner: str, name: str, delta: relativedelta, batchDates: List[datetime],startDate, endDate
):
    # Cynthia_code_begins
    if os.path.getsize('cursor.csv') == 0:
        query = buildPrRequestQuery(owner, name, None)

    else:
        with open('cursor.csv', 'r') as file:
            csv_reader = csv.reader(file)
            last_row = list(csv_reader)[-1]
            cursor = ''.join(last_row)
            
        query = buildPrRequestQuery(owner, name, cursor)
    # Cynthia_code_ends

    # Cynthia_comment_out
    # # prepare batches
    # batches = []
    # batch = None
    # batchStartDate = None
    # batchEndDate = None

    # Cynthia_code_begins
     # prepare batches
    batches = []
    batch = []
    batchStartDate = startDate
    batchEndDate = endDate

    # startDate = datetime.strptime(startDate, "%Y-%m-%d")
    # endDate = datetime.strptime(endDate, "%Y-%m-%d")
    end_date = endDate
    startDate = int(startDate.timestamp())
    endDate = int(endDate.timestamp())

    n = 1
    # Cynthia_code_ends

    while True:
        #Cynthia_code_begins

        if n > int(endDate):
            break 
        #Cynthia_code_ends

        # get page
        result = gql.runGraphqlRequest(pat, query)
        
        print("...")

        # extract nodes
        nodes = result["repository"]["pullRequests"]["nodes"]

        # add results
        for node in nodes:

            createdAt = isoparse(node["createdAt"])
            print(createdAt)
            closedAt = (
                datetime.now(timezone.utc)
                if node["closedAt"] is None
                else isoparse(node["closedAt"])
            )

            # Cynthia_code_begins
            createdAt1 = int(createdAt.timestamp())
            n = createdAt1
            if(
                createdAt1 < int(endDate) and createdAt1 > int(startDate)
            ):
            # Cynthia_code_ends

            # if batchEndDate == None or (
            #     createdAt > batchEndDate and len(batches) < len(batchDates) - 1
            # ):

                print("\n\PR entering the if condition when it is within the time period.")
                print('createdAt1 : ', createdAt)
                print('batch start date: ', batchStartDate)
                print('batch end date: ', end_date)

                if batch is None:
                    batch = []

                # Cynthia_comment_out
                # batchStartDate = batchDates[len(batches)]
                # batchEndDate = batchStartDate + delta

                # batch = []
                

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

                batch.append(pr)

        # check for next page
        pageInfo = result["repository"]["pullRequests"]["pageInfo"]
        if not pageInfo["hasNextPage"]:
            break

        cursor = pageInfo["endCursor"]
        print(cursor)
        query = buildPrRequestQuery(owner, name, cursor)

        # Cynthia_code_begins
        cursor_to_csv(cursor, cursor_file_path)
        #Cynthia_code_ends

    if batch != None:
        batches.append(batch)

    return batches


def buildPrRequestQuery(owner: str, name: str, cursor: str):
    return """{{
        repository(owner: "{0}", name: "{1}") {{
            pullRequests(first:30{2}) {{
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
