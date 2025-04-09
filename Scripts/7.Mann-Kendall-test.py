import pymannkendall as mk
import pandas as pd
import os

# Example data (Replace with your actual data)
directoy = 'cs+satd-datasets'

for dirpath, dirnames, filenames in os.walk(directoy):
    for filename in filenames:
        print("\nFile:", filename)
        df = pd.read_csv(os.path.join(dirpath, filename))
        community_smells = df['PDE']
        satd_counts = df['SATD']
            
        # Mann-Kendall Test for Community Smells
        result_smells = mk.original_test(community_smells)
        print("Community Smells Trend:", result_smells)

        # Mann-Kendall Test for SATD
        result_satd = mk.original_test(satd_counts)
        print("SATD Trend:", result_satd)
