import io
import os
import csv
import math
import sys
from random import randint
import statsAnalysis as stats
import sentistrength
import graphqlAnalysis.graphqlAnalysisHelper as gql
import centralityAnalysis_Cynthia_EndDate as centrality
from functools import reduce
from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse
from typing import List
from datetime import date, datetime, timezone
from configuration import Configuration
import threading
from collections import Counter
from perspectiveAnalysis import getToxicityPercentage
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

cursor_file_path = 'cursor_issue.csv'

def issueAnalysis(
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

    print("Querying issue comments")
    batches = issueRequest(
        config.pat, config.repositoryOwner, config.repositoryName, delta, batchDates, batchStartDate, batchEndDate
    )
 
    batchParticipants = list()
    batchComments = list()

    for batchIdx, batch in enumerate(batches):
        print(f"Analyzing issue batch #{batchIdx}")

        # extract data from batch
        issueCount = len(batch)
        participants = list(
            issue["participants"] for issue in batch if len(issue["participants"]) > 0
        )
        batchParticipants.append(participants)

        allComments = list()
        issuePositiveComments = list()
        issueNegativeComments = list()
        generallyNegative = list()

        print(f"    Sentiments per issue", end="")

        semaphore = threading.Semaphore(15)
        threads = []
        for issue in batch:
            comments = list(
                comment for comment in issue["comments"] if comment and comment.strip()
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
                issuePositiveComments.append(0)
                issueNegativeComments.append(0)
                continue

            allComments.extend(comments)

            thread = threading.Thread(
                target=analyzeSentiments,
                args=(
                    senti,
                    comments,
                    issuePositiveComments,
                    issueNegativeComments,
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
        if issueCount == 0:
            generallyNegativeRatio = 0
        #Cynthia_code_ends
        else:
            generallyNegativeRatio = len(generallyNegative) / issueCount

        # get pr duration stats
        durations = [(pr["closedAt"] - pr["createdAt"]).days for pr in batch]

        print("    All sentiments")

        # analyze comment issue sentiment
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

        centrality.buildGraphQlNetwork(batchIdx, participants, "Issues", config)

        print("Writing GraphQL analysis results")
        with open(
            os.path.join(config.resultsPath, f"results_{batchIdx}.csv"),
            "a",
            newline="",
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow(["NumberIssues", len(batch)])
            w.writerow(["NumberIssueComments", len(allComments)])
            w.writerow(["IssueCommentsPositive", commentSentimentsPositive])
            w.writerow(["IssueCommentsNegative", commentSentimentsNegative])
            w.writerow(["IssueCommentsNegativeRatio", generallyNegativeRatio])
            w.writerow(["IssueCommentsToxicityPercentage", toxicityPercentage])

        # Cynthia_comment_out
        with open(
            os.path.join(config.metricsPath, f"issueCommentsCount_{batchIdx}.csv"),
            "a",
            newline="",
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow(["Issue Number", "Comment Count"])
            for issue in batch:
                w.writerow([issue["number"], len(issue["comments"])])

        with open(
            os.path.join(config.metricsPath, f"issueParticipantCount_{batchIdx}.csv"),
            "a",
            newline="",
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow(["Issue Number", "Developer Count"])
            for issue in batch:
                w.writerow([issue["number"], len(set(issue["participants"]))])

        # output statistics
        stats.outputStatistics(
            batchIdx,
            commentLengths,
            "IssueCommentsLength",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            durations,
            "IssueDuration",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            [len(issue["comments"]) for issue in batch],
            "IssueCommentsCount",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            commentSentiments,
            "IssueCommentSentiments",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            [len(set(issue["participants"])) for issue in batch],
            "IssueParticipantCount",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            issuePositiveComments,
            "IssueCountPositiveComments",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            issueNegativeComments,
            "IssueCountNegativeComments",
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


def issueRequest(
    pat: str, owner: str, name: str, delta: relativedelta, batchDates: List[datetime], startDate, endDate
):

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

    cursor = None
    while True:

        if n > int(endDate):
            break

        # get page of Issues
        if os.path.getsize('cursor_issue.csv') == 0:
            query = buildIssueRequestQuery(owner,name,None)
        else:
            with open('cursor_issue.csv', 'r') as file:
                csv_reader = csv.reader(file)
                last_row = list(csv_reader)[-1]
                cursor = ''.join(last_row)
            query = buildIssueRequestQuery(owner, name, cursor)

        result = gql.runGraphqlRequest(pat, query)

        

        print("...")
    

        # extract nodes
        nodes = result["repository"]["issues"]["nodes"]

        # analyse
        for node in nodes:

            createdAt = isoparse(node["createdAt"])
            closedAt = (
                datetime.now(timezone.utc)
                if node["closedAt"] is None
                else isoparse(node["closedAt"])
            )

            # Cynthia_EndDate
            createdAt1 = int(createdAt.timestamp())
            n = createdAt1

            if(
                createdAt1 < int(endDate) and createdAt1 > int(startDate)
            ):

            # if batchEndDate == None or (
            #     createdAt > batchEndDate and len(batches) < len(batchDates) - 1
            # ):

                # print("\n\nissue entering the if condition when it is within the time period.")
                print('createdAt1 : ', createdAt)
                print('batch start date: ', batchStartDate)
                print('batch end date: ', end_date)

                if batch is None:
                    batch = []

                # batchStartDate = batchDates[len(batches)]
                # batchEndDate = batchStartDate + delta

                # batch = []

                issue = {
                    "number": node["number"],
                    "createdAt": createdAt,
                    "closedAt": closedAt,
                    "comments": list(c["bodyText"] for c in node["comments"]["nodes"]),
                    "participants": list(),
                }

                
                # participants
                for user in node["participants"]["nodes"]:
                    gql.addLogin(user, issue["participants"])

                batch.append(issue)
                

        # check for next page
        pageInfo = result["repository"]["issues"]["pageInfo"]
        if not pageInfo["hasNextPage"]:
            break

        cursor = pageInfo["endCursor"]
        cursor_to_csv(cursor, cursor_file_path)


    if batch != None:
        batches.append(batch)
    
    return batches





def buildIssueRequestQuery(owner: str, name: str, cursor: str):
    return """{{
        repository(owner: "{0}", name: "{1}") {{
            issues(first: 30{2}) {{
                pageInfo {{
                    hasNextPage
                    endCursor
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
                    comments(first: 100) {{
                        nodes {{
                            bodyText
                        }}
                    }}
                }}
            }}
        }}
    }}""".format(
        owner, name, gql.buildNextPageQuery(cursor)
    )