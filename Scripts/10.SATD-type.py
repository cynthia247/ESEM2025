import pandas as pd

def merge_SATD_result(repo):
    df1 = pd.read_csv(f'mt-bert-satd-tool/results/predict_{repo}_filtered_comments.csv')
    df2 = pd.read_csv(f'comments/{repo}_filtered_comments.csv')
    df2['SATD'] = df1['predict'].values
    
    return df2


# Add the type of the SATDs in the next columns. 
# Group the types of SATDs and sum them up.
# Combine a new csv file with community smells present in that release along with total number of SATDs and the predicted SATD types.


def grouping_SATD(df):

    satd_summary = df.groupby('Version')['SATD'].sum().reset_index()
    satd_summary = satd_summary.rename(columns={'Version': 'Release'})
  

    return satd_summary


if __name__ == "__main__":
    df = pd.read_csv('csDetector-Result/Repos-with-release.csv')
    for i, row in df.iterrows():
        # if i == 1: break
        owner = row['owner']
        repo = row['repo']
        
        GITHUB_REPO = owner + '/' + repo
      
        # repo = 'MaixPy'

        print("\n")
        print(f"Processing {repo}")
        print("######### Merging SATD result #########")
        new_satd_df = merge_SATD_result(repo)
        print(new_satd_df.head)

        print("######### Grouping SATD #########")
        satd_summary = grouping_SATD(new_satd_df)
        print(satd_summary.head())