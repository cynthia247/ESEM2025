# import pandas as pd
# import statsmodels.api as sm
# import statsmodels.formula.api as smf
# from scipy.stats import spearmanr
# import pandas as pd
# from scipy.stats import pointbiserialr, spearmanr, mannwhitneyu

# # Create DataFrame from your subse
# df = pd.read_csv('satd-datasets/tesseract_satd_type.csv')

# # Point-biserial correlation between Radio Silence and Design Debt
# r_pb, p_value = pointbiserialr(df['RS'], df['Design'])
# print(f"Point-biserial correlation (RS vs Design): r = {r_pb:.3f}, p = {p_value:.3f}")


import os
import pandas as pd
from scipy.stats import pointbiserialr

# === STEP 1: Set your dataset directory path ===
data_dir = "satd-datasets/satd-type"  # 🔁 <- Change this to the folder path

# === STEP 2: Define smell and SATD columns ===
community_smells = ['OSE', 'BCE', 'PDE', 'SV', 'OS', 'SD', 'RS', 'TF', 'UI', 'TC']
satd_types = ['Code', 'Defect', 'Design', 'Documentation', 'M&T', 'Requirement']

# === STEP 3: Collect results here ===
results = []

# === STEP 4: Iterate over each CSV file (project) ===
for filename in os.listdir(data_dir):
    if filename.endswith(".csv"):
        filepath = os.path.join(data_dir, filename)
        try:
            df = pd.read_csv(filepath)
            project_name = df['Project_names'].iloc[0] if 'Project_names' in df.columns else filename.replace('.csv', '')

            for smell in community_smells:
                if smell in df.columns:
                    for satd in satd_types:
                        if satd in df.columns:
                            # Check if there is enough variance
                            if df[smell].nunique() > 1 and df[satd].nunique() > 1:
                                r, p = pointbiserialr(df[smell], df[satd])
                                results.append({
                                    'Project': project_name,
                                    'CommunitySmell': smell,
                                    'SATD_Type': satd,
                                    'Correlation': round(r, 3),
                                    'P_Value': round(p, 4)
                                })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# === STEP 5: Create DataFrame of results ===
result_df = pd.DataFrame(results)

# === STEP 6: Save to CSV ===
output_file = 'Scripts/smell_satd_correlation_results.csv'
result_df.to_csv(output_file, index=False)
print(f"✅ Results saved to: {output_file}")

positive_corr_df = result_df[(result_df['Correlation'] > 0) & (result_df['P_Value'] < 0.05)]
# === STEP 8: Save positive correlation results ===
output_positive = 'Scripts/positive_correlations_only.csv'
positive_corr_df.to_csv(output_positive, index=False)
print(f"✅ Positive correlations saved to: {output_positive}")
