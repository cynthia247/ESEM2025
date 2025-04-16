import pandas as pd
import numpy as np

def quartile_analysis(df):
    """
    Perform quartile analysis on predefined smell columns in the DataFrame.
    Returns a new DataFrame with the following statistics:
    - Lower Whisker
    - Lower Quartile (Q1)
    - Median
    - Average
    - Upper Quartile (Q3)
    - Upper Whisker
    - Standard Deviation
    """
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

# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("Scripts/Community-smell-combined-result.csv")

    small_df = df.iloc[0:82] 
    medium_df = df.iloc[90:136]
    large_df = df.iloc[145:176]

    print("Small Projects Quartile Analysis:")
    result_small = quartile_analysis(small_df) 
    print(result_small)

    print("\nMedium Projects Quartile Analysis:")
    result_medium = quartile_analysis(medium_df)  
    print(result_medium)

    print("\nLarge Projects Quartile Analysis:")
    result_large = quartile_analysis(large_df)  
    print(result_large)
