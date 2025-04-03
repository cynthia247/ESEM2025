import pandas as pd
from scipy.stats import spearmanr
import os 

# def correlation_analysis(repo):

#     df = pd.read_csv(f'cs+satd-datasets/{repo}_cs+satd.csv')

#     # Spearman correlation
#     corr, p_value = spearmanr(df['CommunitySmells'], df['SATD'])

#     print(f"Spearman correlation coefficient (ρ): {corr:.3f}")
#     print(f"P-value: {p_value:.3f}")

#     if p_value < 0.05:
#         print("✅ Significant correlation found!")
#     else:
#         print("❌ No significant correlation found.")

# def all_repo_correlation_analysis(csv_files):
#     combined_df = pd.read_csv(csv_files[0])

#     for file in csv_files[1:]:
#         df = pd.read_csv(file, header=0)
#         combined_df = pd.concat([combined_df, df], ignore_index=True)
    
#     print(combined_df)
#     # combined_df.to_csv('cs+satd-datasets/combined_cs+satd.csv', index=False)
#     # combined_df = combined_df.iloc[116:]
#     # Spearman correlation
#     corr, p_value = spearmanr(combined_df['CommunitySmells'], combined_df['SATD'])

#     print(f"Spearman correlation coefficient (ρ): {corr:.3f}")
#     print(f"P-value: {p_value:.3f}")

#     if p_value < 0.05:
#         print("✅ Significant correlation found!")
#     else:
#         print("❌ No significant correlation found.")



# if __name__ == "__main__":
#     df = pd.read_csv('csDetector-Result-v2/project_names.csv')
#     csv_files = []
#     for i, row in df.iterrows():
#         # if i == 1: break
#         owner = row['owner']
#         repo = row['repo']
#         print(repo)
        
#         if not os.path.exists(f'cs+satd-datasets/{repo}_cs+satd.csv'):
#             continue
#         print("\n")
#         print(f"Analyzing {owner}/{repo}...")
#         GITHUB_REPO = owner + '/' + repo
#         correlation_analysis(repo)
#         csv_files.append(f'cs+satd-datasets/{repo}_cs+satd.csv')
#     print(csv_files)
#     all_repo_correlation_analysis(csv_files)




directoy = 'cs+satd-datasets'

for dirpath, dirnames, filenames in os.walk(directoy):
    for filename in filenames:
        print("\nFile:", filename)
        df = pd.read_csv(os.path.join(dirpath, filename))
        community_smells = df['CommunitySmells']
        satd_counts = df['SATD']
            
        corr, p_value = spearmanr(df['CommunitySmells'], df['SATD'])

        print(f"Spearman correlation coefficient (ρ): {corr:.3f}")
        print(f"P-value: {p_value:.3f}")

        if p_value < 0.05:
            print("✅ Significant correlation found!")
        else:
            print("❌ No significant correlation found.")