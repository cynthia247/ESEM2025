import os
import csv

import numpy as np

from configuration import Configuration


def devAnalysis(
    authorInfoDict: set, batchIdx: np.int64, devs: set, coreDevs: set, config: Configuration
):

    # select experienced developers
    experiencedDevs = [
        login
        for login, author in authorInfoDict.items()
        if author["experienced"] == True
    ]

    # filter by developers present in list of aliased developers by commit
    numberActiveExperiencedDevs = len(devs.intersection(set(experiencedDevs)))

    # calculate bus factor
    # Cynthia
    if len(devs) > 0:
        busFactor = (len(devs) - len(coreDevs)) / len(devs)
    else:
        busFactor = 0

    # calculate TFC
    commitCount = sum(
        [author["commitCount"] for login, author in authorInfoDict.items()]
    )
    sponsoredCommitCount = sum(
        [
            author["commitCount"]
            for login, author in authorInfoDict.items()
            if author["sponsored"] == True
        ]
    )
    experiencedCommitCount = sum(
        [
            author["commitCount"]
            for login, author in authorInfoDict.items()
            if author["experienced"] == True
        ]
    )

    sponsoredTFC = sponsoredCommitCount / commitCount * 100
    experiencedTFC = experiencedCommitCount / commitCount * 100

    print("Writing developer analysis results")
    with open(
        os.path.join(config.resultsPath, f"results_{batchIdx}.csv"), "a", newline=""
    ) as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["NumberActiveExperiencedDevs", numberActiveExperiencedDevs])
        w.writerow(["BusFactorNumber", busFactor])
        w.writerow(["SponsoredTFC", sponsoredTFC])
        w.writerow(["ExperiencedTFC", experiencedTFC])