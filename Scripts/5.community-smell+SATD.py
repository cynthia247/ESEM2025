import pandas as pd

def merge_SATD_result(repo):
    df1 = pd.read_csv(f'mt-bert-satd-tool/results/predict_{repo}_filtered_comments.csv')
    df2 = pd.read_csv(f'comments/{repo}_filtered_comments.csv')
    df2['SATD'] = df1['predict'].values

    return df2

def grouping_SATD(df):

    satd_summary = df.groupby('Version')['SATD'].sum().reset_index()
    satd_summary = satd_summary.rename(columns={'Version': 'Release'})

    return satd_summary

def merge_community_smell_SATD(satd_df,repo):
    cs_df = pd.read_csv(f'csDetector-Result/{repo}_combined-result.csv')

    merged_df = cs_df.merge(satd_df, on="Release", how="left")

    smell_columns = ['OSE', 'BCE', 'PDE', 'SV', 'OS', 'SD', 'RS', 'TF', 'UI', 'TC']
    merged_df['CommunitySmells'] = merged_df[smell_columns].sum(axis=1)

    cols = merged_df.columns.tolist()
    tc_index = cols.index('TC')
    cols = cols[:tc_index+1] + ['CommunitySmells'] + cols[tc_index+1:-1]
    merged_df = merged_df[cols + ['SATD']]

    merged_df.to_csv(f'cs+satd-datasets/{repo}_cs+satd.csv', index=False)
    print('merged result to: ', f'cs+satd-datasets/{repo}_cs+satd.csv')
    return merged_df


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

        print("\n")
        print("######### Merging community-smell+SATD #########")
        cs_satd_df = merge_community_smell_SATD(satd_summary, repo)
        print(cs_satd_df.head())