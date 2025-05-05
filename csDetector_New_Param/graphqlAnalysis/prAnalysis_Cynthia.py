import math
import os
import csv
import sys
import json 

import pandas as pd
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
import pickle
from graphqlAnalysis.automation_Cynthia import command_automation
import pytz


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

    #Cynthia
    prRequest(config.pat, config.repositoryOwner, config.repositoryName, delta, batchDates, batchStartDate, batchEndDate)
    

    batches = []
    with open('batch_list_file.pkl', 'rb') as pickle_file:
        try:
            while True:
                item = pickle.load(pickle_file)
                batches.append(item)
        except EOFError:
            pass  # Reached the end of the file
        
    batchParticipants = list()
    batchComments = list()

    for batchIdx, batch in enumerate(batches):
        print(f"Analyzing PR batch #{batchIdx}")

        
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

        generallyNegativeRatio = len(generallyNegative) / prCount

        # get pr duration stats
        # Cynthia
        # date_obj1 = datetime.strptime(pr["closedAt"], "%d/%m/%Y")
        # date_obj2 = datetime.strptime(pr["createdAt"], "%d/%m/%Y")
        # durations = [(date_obj1 - date_obj2).days for pr in batch]
        if pr['closedAt'] != None:
            durations = [(pr["closedAt"] - pr["createdAt"]).days for pr in batch]
        else:
            date_obj1 = datetime.strptime(pr["closedAt"], "%d/%m/%Y")
            date_obj2 = datetime.strptime(pr["createdAt"], "%d/%m/%Y")
            durations = [(date_obj1 - date_obj2).days for pr in batch]

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

        # Cynthia_comment_out
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

    batchcomments = []
    batchcomments.append(batchComments)
    return batchParticipants, batchcomments


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


# Cynthia
def write_to_csv(data, file_path):
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



csv_file_path = "example.csv"
def prRequest(
    pat: str, owner: str, name: str, delta: relativedelta, batchDates: List[datetime], batchStartDate, batchEndDate
):
    command_automation(
        pat, owner, name, delta, batchDates, batchStartDate, batchEndDate
        )
