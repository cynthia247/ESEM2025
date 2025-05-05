import os
import csv
import graphqlAnalysis.graphqlAnalysisHelper as gql
import dateutil
import git
import statsAnalysis as stats
from typing import List
from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse
from datetime import datetime
from configuration import Configuration
import pytz

def releaseAnalysis(
    allCommits: List[git.Commit],
    config: Configuration,
    delta: relativedelta,
    batchDates: List[datetime],
):

    # sort commits by ascending commit date
    allCommits.sort(key=lambda c: c.committed_datetime )
    
    if config.startDate is not None:
        startDate = datetime.strptime(config.startDate, "%Y-%m-%d")
        startDate = startDate.replace(tzinfo=pytz.UTC)
    batchStartDate = startDate

    if config.endDate is not None:
        endDate = datetime.strptime(config.endDate, "%Y-%m-%d")
        endDate = endDate.replace(tzinfo=pytz.UTC)

    batchEndDate = endDate

    print("Querying releases")
    batches = releaseRequest(config, delta, batchDates, startDate, endDate)

    for batchIdx, batch in enumerate(batches):

        releases = batch["releases"]
        releaseAuthors = set()
        releaseCommitsCount = {}
        release_commit =[]
        for i, release in enumerate(releases):
            releaseCommits = list()
            
            releaseDate = release["createdAt"]
            # try add author to set
            releaseAuthors.add(release["author"])
            n = 0
            if i == 0:

                # this is the first release, get all commits prior to release created date
                for commit in allCommits:
                    if commit.committed_datetime < releaseDate:
                        releaseCommits.append(commit)
                    # else:
                    #     break

            else:
                # get in-between commit count
                prevReleaseDate = releases[i - 1]["createdAt"]
                
                for commit in allCommits:     
                    
                    if (
                        commit.committed_datetime >= prevReleaseDate and commit.committed_datetime < releaseDate
                    ):           
                        release_commit.append(commit)
                    
                    # else:
                    #     break
              
            # remove all counted commits from list to improve iteration speed
            allCommits = allCommits[len(releaseCommits) :]
            

            # calculate authors per release
            commitAuthors = set(commit.author.email for commit in releaseCommits)

            # add results
            releaseCommitsCount[release["name"]] = dict(
                    date=release["createdAt"],
                    authorsCount=len(commitAuthors),
                    commitsCount=len(release_commit),
                )

        # sort releases by date ascending
        releaseCommitsCount = {
            key: value
            for key, value in sorted(
                releaseCommitsCount.items(), key=lambda r: r[1]["date"]
            )
        }

        print("Writing results")
        with open(
            os.path.join(config.resultsPath, f"results_{batchIdx}.csv"), "a", newline=""
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow(["NumberReleases", batch["releaseCount"]])
            w.writerow(["NumberReleaseAuthors", len(releaseAuthors)])

        with open(
            os.path.join(config.metricsPath, f"releases_{batchIdx}.csv"),
            "a",
            newline="",
        ) as f:
            w = csv.writer(f, delimiter=",")
            w.writerow(["Release", "Date", "Author Count", "Commit Count"])
            for key, value in releaseCommitsCount.items():
                w.writerow(
                    [
                        key,
                        value["date"].isoformat(),
                        value["authorsCount"],
                        value["commitsCount"],
                    ]
                )

        stats.outputStatistics(
            batchIdx,
            [value["authorsCount"] for key, value in releaseCommitsCount.items()],
            "ReleaseAuthorCount",
            config.resultsPath,
        )

        stats.outputStatistics(
            batchIdx,
            [value["commitsCount"] for key, value in releaseCommitsCount.items()],
            "ReleaseCommitCount",
            config.resultsPath,
        )


def releaseRequest(
    config: Configuration, delta: relativedelta, batchDates: List[datetime], startDate, endDate
):
    query = buildReleaseRequestQuery(
        config.repositoryOwner, config.repositoryName, None
    )

    # prepare batches
    batches = []
    batch = None
    batchStartDate = startDate
    batchEndDate = endDate

    end_date = endDate
    startDate = int(startDate.timestamp())
    endDate = int(endDate.timestamp())
    n = 1

    while True:

        # get page of releases
        result = gql.runGraphqlRequest(config.pat, query)

        #Cynthia_code_begins

        if n > int(endDate):
            break
        #Cynthia_code_ends

        # extract nodes
        nodes = result["repository"]["releases"]["nodes"]
        nodes = sorted(nodes, key=lambda x: datetime.fromisoformat(x['createdAt'].replace('Z', '+00:00')))
        
        # parse
        for node in nodes:

            createdAt = isoparse(node["createdAt"])

            # Cynthia_EndDate
            createdAt1 = int(createdAt.timestamp())
            n = createdAt1

            if(
                createdAt1 < int(endDate) and createdAt1 > int(startDate)
            ):
                
            # if batchEndDate == None or (
            #     createdAt > batchEndDate and len(batches) < len(batchDates) - 1
            # ):
                # print("\n\ release entering the if condition when it is within the time period.")
                # print('createdAt1 : ', createdAt)
                # print('batch start date: ', batchStartDate)
                # print('batch end date: ', end_date)


                # if batch != None:
                #     batches.append(batch)
                #     # batch = []
                if batch is None:
                    batch = {"releaseCount": 0, "releases": []}

                # batchStartDate = batchDates[len(batches)]
                # batchEndDate = batchStartDate + delta

                # batch = {"releaseCount": 0, "releases": []}

                batch["releaseCount"] += 1
                batch["releases"].append(
                    dict(
                        name=node["name"],
                        createdAt=createdAt,
                        author=node["author"]["login"],
                    )
                )
                
        # check for next page
        pageInfo = result["repository"]["releases"]["pageInfo"]
        if not pageInfo["hasNextPage"]:
            break

        cursor = pageInfo["endCursor"]
        query = buildReleaseRequestQuery(
            config.repositoryOwner, config.repositoryName, cursor
        )

    if batch != None:
        batches.append(batch)
        
    return batches


def buildReleaseRequestQuery(owner: str, name: str, cursor: str):
    return """{{
        repository(owner: "{0}", name: "{1}") {{
            releases(first:100{2}) {{
                totalCount
                nodes {{
                    author {{
                        login
                    }}
                    createdAt
                    name
                }}
                pageInfo {{
                    endCursor
                    hasNextPage
                }}
            }}
        }}
    }}""".format(
        owner, name, gql.buildNextPageQuery(cursor)
    )
