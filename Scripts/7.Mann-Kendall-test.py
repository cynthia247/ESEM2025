import pymannkendall as mk
import pandas as pd

# Example data (Replace with your actual data)
df = pd.read_csv('cs+satd-datasets/tesseract_cs+satd.csv')
community_smells = df['OS']
satd_counts = df['SATD']

# Mann-Kendall Test for Community Smells
result_smells = mk.original_test(community_smells)
print("Community Smells Trend:", result_smells)

# Mann-Kendall Test for SATD
result_satd = mk.original_test(satd_counts)
print("SATD Trend:", result_satd)
