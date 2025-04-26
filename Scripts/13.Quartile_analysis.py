import pandas as pd
import numpy as np

def quartile_analysis(df):
    smell_columns = ['OSE', 'BCE', 'PDE', 'SV', 'OS', 'SD', 'RS', 'TF', 'UI', 'TC']
    summary = []

    for column in smell_columns:
        if column in df.columns:
            # Force numeric conversion (non-convertible values become NaN)
            data = pd.to_numeric(df[column], errors='coerce').dropna()

            if len(data) == 0:
                print(f"⚠️ Column '{column}' has no valid numeric data.")
                continue

            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            median = np.median(data)
            avg = np.mean(data)
            stddev = np.std(data, ddof=1)
            iqr = q3 - q1
            lower_whisker = max(data.min(), q1 - 1.5 * iqr)
            upper_whisker = min(data.max(), q3 + 1.5 * iqr)

            summary.append({
                'Feature': column,
                'Lower Whisker': lower_whisker,
                'Lower Quartile (Q1)': q1,
                'Median': median,
                'Average': avg,
                'Upper Quartile (Q3)': q3,
                'Upper Whisker': upper_whisker,
                'Standard Deviation': stddev
            })
        else:
            print(f"⚠️ Skipping column '{column}': Not found in DataFrame.")

    return pd.DataFrame(summary)


def satd_quartile_analysis(df):
    satd_columns = ['Code',	'Defect',	'Design',	'Documentation',	'M&T'	,'Requirement']
    summary = []

    for column in satd_columns:
        if column in df.columns:
            # Force numeric conversion (non-convertible values become NaN)
            data = pd.to_numeric(df[column], errors='coerce').dropna()

            if len(data) == 0:
                print(f"⚠️ Column '{column}' has no valid numeric data.")
                continue

            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            median = np.median(data)
            avg = np.mean(data)
            stddev = np.std(data, ddof=1)
            iqr = q3 - q1
            lower_whisker = max(data.min(), q1 - 1.5 * iqr)
            upper_whisker = min(data.max(), q3 + 1.5 * iqr)

            summary.append({
                'Feature': column,
                'Lower Whisker': lower_whisker,
                'Lower Quartile (Q1)': q1,
                'Median': median,
                'Average': avg,
                'Upper Quartile (Q3)': q3,
                'Upper Whisker': upper_whisker,
                'Standard Deviation': stddev
            })
        else:
            print(f"⚠️ Skipping column '{column}': Not found in DataFrame.")

    return pd.DataFrame(summary)

from scipy.stats import kruskal
# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("Scripts/Community-smell-combined-result.csv")

    small_df = df.iloc[0:82] 
    medium_df = df.iloc[90:136]
    large_df = df.iloc[145:176]

    print("Small Projects Quartile Analysis:")
    cs_result_small = quartile_analysis(small_df) 
    print(cs_result_small)

    print("\nMedium Projects Quartile Analysis:")
    cs_result_medium = quartile_analysis(medium_df)  
    print(cs_result_medium)

    print("\nLarge Projects Quartile Analysis:")
    cs_result_large = quartile_analysis(large_df)  
    print(cs_result_large)

    from scipy.stats import kruskal

    stat, p = kruskal(small_df['BCE'], medium_df['BCE'], large_df['BCE'])
    print(f"Kruskal-Wallis H-statistic: {stat}, p-value: {p}")


    # small_satd_df = pd.read_csv("satd-datasets/1.small-projects.csv")
    # print("Small Projects Quartile Analysis:")
    # satd_result_small = satd_quartile_analysis(small_satd_df)
    # print(satd_result_small)

    # medium_satd_df = pd.read_csv("satd-datasets/2.medium-projects.csv")
    # print("Medium Projects Quartile Analysis:")
    # satd_result_medium = satd_quartile_analysis(medium_satd_df)
    # print(satd_result_medium)

    # large_satd_df = pd.read_csv("satd-datasets/3.large-projects.csv")
    # print("Large Projects Quartile Analysis:")
    # satd_result_large = satd_quartile_analysis(large_satd_df)
    # print(satd_result_large)
