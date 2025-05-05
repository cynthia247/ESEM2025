import pandas as pd
import pymannkendall as mk
import os

# Directory with your CSV files
data_dir = "satd-datasets/satd-type"
project_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

# Define column categories
smell_columns = ['OSE', 'BCE', 'PDE', 'SV', 'OS', 'SD', 'RS', 'TF', 'UI', 'TC']
satd_columns = ['Code', 'Defect', 'Design', 'Documentation', 'M&T', 'Requirement']
all_columns = smell_columns + satd_columns

# Initialize results table
results_df = pd.DataFrame(index=all_columns)

# Function to compute trend and format results
def run_mk_trend(series):
    try:
        result = mk.original_test(series)
        arrow = "↑" if result.trend == "increasing" else "↓" if result.trend == "decreasing" else "–"
        stars = (
            "***" if result.p < 0.001 else
            "**" if result.p < 0.01 else
            "*" if result.p < 0.05 else ""
        )
        return f"{result.s}[{arrow}]{stars}"
    except Exception:
        return ""

# Analyze each project file
for file in project_files:
    project_name = file.replace("_satd_type.csv", "")
    df = pd.read_csv(os.path.join(data_dir, file))
    df['Time'] = range(1, len(df) + 1)

    col_results = []
    for col in all_columns:
        if col in df.columns:
            trend_result = run_mk_trend(df[col])
            col_results.append(trend_result)
        else:
            col_results.append("")

    results_df[project_name] = col_results

# Save result
results_df.to_csv("mk_trend_summary.csv")
print("✅ Saved to mk_trend_summary.csv")
