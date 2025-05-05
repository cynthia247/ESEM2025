from statistics import *
import os
import csv

import numpy as np


def outputStatistics(idx: np.int64, data: list, metric: str, outputDir: str):

    # validate
    if len(data) < 1:
        return

    # calculate and output
    stats = calculateStats(data)

    # output
    with open(os.path.join(outputDir, f"results_{idx}.csv"), "a", newline="") as f:
        w = csv.writer(f, delimiter=",")

        for key in stats:
            outputValue(w, metric, key, stats)


def calculateStats(data):

    #Cynthia
    stats = dict(
        # count=len(data),
        # mean=mean(list(map(int, data))),
        # stdev=stdev(list(map(int, data))) if len(data) > 1 else None
        count=len(data),
        mean=mean(data) if len(data) > 1 else 0,
        stdev=stdev(data) if len(data) > 1 else None
    )

    return stats


def outputValue(w, metric: str, name: str, dict: dict):
    value = dict[name]
    name = "{0}_{1}".format(metric, name)
    w.writerow([name, value])
