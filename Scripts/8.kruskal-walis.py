import pandas as pd
import numpy as np
from scipy.stats import kruskal
import scikit_posthocs as sp
import os

# Step 1: Define ML and Non-ML Projects
project_ml = [
    'bigartm_cs+satd', 'coco-annotator_cs+satd', 'PyKEEN_cs+satd', 'POT_cs+satd',  # Small
    'pyro_cs+satd', 'ludwig_cs+satd', 'hdbscan_cs+satd', 'compromise_cs+satd',  # Medium
    'tesseract_cs+satd', 'incubator-mxnet_cs+satd', 'shap_cs+satd', 'mne-python_cs+satd'  # Large
]

project_nonml = [
    'viser', 'photonix', 'fastapi-crudrouter', 'ElevenClock',  # Small
    'sqladmin', 'Robyn', 'jquery-pjax', 'api',  # Medium
    'glances', 'oauthlib'  # Large (only 10 projects)
]

# Base directory containing subdirectories
data_dir = 'Project-types/'  # Replace with your actual path, e.g., 'C:/research/data/'

# Step 2: Function to Calculate Average Frequencies from CSV
def calculate_avg_frequencies(file_path, project_name):
    df = pd.read_csv(file_path)
    num_releases = len(df)
    smells = ['OSE', 'BCE', 'PDE', 'SV', 'OS', 'SD', 'RS', 'TF', 'UI', 'TC']
    avg_frequencies = {}
    for smell in smells:
        if smell in df.columns:
            avg_frequencies[smell] = df[smell].sum() / num_releases
        else:
            avg_frequencies[smell] = 0  # Handle missing columns
    return {'Project': project_name, **avg_frequencies}

# Step 3: Process All Projects and Assign Sizes from Subdirectories
ml_data = []
nonml_data = []
sizes = ['small', 'medium', 'large']

for size in sizes:
    sub_dir = os.path.join(data_dir, size)
    if not os.path.exists(sub_dir):
        print(f"Warning: Directory {sub_dir} not found")
        continue
    
    for file_name in os.listdir(sub_dir):
        if file_name.endswith('.csv'):
            project_name = file_name.replace('.csv', '')
            file_path = os.path.join(sub_dir, file_name)
            
            # Calculate averages
            avg_freq = calculate_avg_frequencies(file_path, project_name)
            avg_freq['Size'] = size.capitalize()  # Capitalize for consistency (Small, Medium, Large)
            
            # Assign to ML or Non-ML based on project lists
            if project_name in project_ml:
                ml_data.append(avg_freq)
            elif project_name in project_nonml:
                nonml_data.append(avg_freq)
            else:
                print(f"Warning: {project_name} not recognized as ML or Non-ML project")
print(ml_data)
# Convert to DataFrames
df_ml = pd.DataFrame(ml_data)
df_nonml = pd.DataFrame(nonml_data)

# Step 4: Kruskal-Wallis Test for ML Projects
smells = ['OSE', 'BCE', 'PDE', 'SV', 'OS', 'SD', 'RS', 'TF', 'UI', 'TC']
results_ml = []

for smell in smells:
    small = df_ml[df_ml['Size'] == 'Small'][smell]
    medium = df_ml[df_ml['Size'] == 'Medium'][smell]
    large = df_ml[df_ml['Size'] == 'Large'][smell]
    
    # Ensure there’s data for all groups
    if len(small) == 0 or len(medium) == 0 or len(large) == 0:
        print(f"Warning: Incomplete data for {smell} in ML projects")
        continue
    
    h_stat, p_val = kruskal(small, medium, large)
    
    posthoc_results = "-"
    if p_val < 0.05:
        data = pd.concat([pd.DataFrame({'value': small, 'group': 'Small'}),
                          pd.DataFrame({'value': medium, 'group': 'Medium'}),
                          pd.DataFrame({'value': large, 'group': 'Large'})])
        posthoc = sp.posthoc_dunn(data, val_col='value', group_col='group', p_adjust='bonferroni')
        significant_pairs = []
        if posthoc.loc['Small', 'Medium'] < 0.05:
            significant_pairs.append(f"Small vs Medium (p={posthoc.loc['Small', 'Medium']:.3f})")
        if posthoc.loc['Small', 'Large'] < 0.05:
            significant_pairs.append(f"Small vs Large (p={posthoc.loc['Small', 'Large']:.3f})")
        if posthoc.loc['Medium', 'Large'] < 0.05:
            significant_pairs.append(f"Medium vs Large (p={posthoc.loc['Medium', 'Large']:.3f})")
        posthoc_results = "; ".join(significant_pairs) if significant_pairs else "-"
    
    results_ml.append({
        'Smell': smell,
        'Small Mean': round(small.mean(), 2) if len(small) > 0 else np.nan,
        'Medium Mean': round(medium.mean(), 2) if len(medium) > 0 else np.nan,
        'Large Mean': round(large.mean(), 2) if len(large) > 0 else np.nan,
        'H-Statistic': round(h_stat, 2),
        'p-Value': round(p_val, 3),
        'Significant Pairs': posthoc_results
    })

# Step 5: Kruskal-Wallis Test for Non-ML Projects
results_nonml = []

for smell in smells:
    small = df_nonml[df_nonml['Size'] == 'Small'][smell]
    medium = df_nonml[df_nonml['Size'] == 'Medium'][smell]
    large = df_nonml[df_nonml['Size'] == 'Large'][smell]
    
    if len(small) == 0 or len(medium) == 0 or len(large) == 0:
        print(f"Warning: Incomplete data for {smell} in Non-ML projects")
        continue
    
    h_stat, p_val = kruskal(small, medium, large)
    
    posthoc_results = "-"
    if p_val < 0.05:
        data = pd.concat([pd.DataFrame({'value': small, 'group': 'Small'}),
                          pd.DataFrame({'value': medium, 'group': 'Medium'}),
                          pd.DataFrame({'value': large, 'group': 'Large'})])
        posthoc = sp.posthoc_dunn(data, val_col='value', group_col='group', p_adjust='bonferroni')
        significant_pairs = []
        if posthoc.loc['Small', 'Medium'] < 0.05:
            significant_pairs.append(f"Small vs Medium (p={posthoc.loc['Small', 'Medium']:.3f})")
        if posthoc.loc['Small', 'Large'] < 0.05:
            significant_pairs.append(f"Small vs Large (p={posthoc.loc['Small', 'Large']:.3f})")
        if posthoc.loc['Medium', 'Large'] < 0.05:
            significant_pairs.append(f"Medium vs Large (p={posthoc.loc['Medium', 'Large']:.3f})")
        posthoc_results = "; ".join(significant_pairs) if significant_pairs else "-"
    
    results_nonml.append({
        'Smell': smell,
        'Small Mean': round(small.mean(), 2) if len(small) > 0 else np.nan,
        'Medium Mean': round(medium.mean(), 2) if len(medium) > 0 else np.nan,
        'Large Mean': round(large.mean(), 2) if len(large) > 0 else np.nan,
        'H-Statistic': round(h_stat, 2),
        'p-Value': round(p_val, 3),
        'Significant Pairs': posthoc_results
    })

# Step 6: Create Output Tables
results_ml_df = pd.DataFrame(results_ml)
results_nonml_df = pd.DataFrame(results_nonml)

print("\nTable 1: Kruskal-Wallis Test Results for ML Projects")
print(results_ml_df.to_string(index=False))

print("\nTable 2: Kruskal-Wallis Test Results for Non-ML Projects")
print(results_nonml_df.to_string(index=False))

# Step 7: Save to CSV
results_ml_df.to_csv('kruskal_wallis_ml.csv', index=False)
results_nonml_df.to_csv('kruskal_wallis_nonml.csv', index=False)