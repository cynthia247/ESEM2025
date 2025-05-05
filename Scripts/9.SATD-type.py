import pandas as pd

def merge_SATD_result(repo):
    
    df1 = pd.read_csv(f'mt-bert-satd-tool/results/predict_{repo}_filtered_comments.csv')
    df2 = pd.read_csv(f'comments/{repo}_filtered_comments.csv')
    df2['SATD'] = df1['predict'].values
    satd_df = df2[df2['SATD'] == 1]
    satd_df.to_csv(f'satd-datasets/{repo}_satd.csv', index=False)

    satd_data_type_predicted = True
    if satd_data_type_predicted:
        df3 = pd.read_csv(f'satd-datasets/{repo}_satd_type.csv')  # Fixed: actually read the CSV
        # print('merged result to: ', f'Scripts/{repo}_satd.csv')

        # # Add the SATD type to the filtered DataFrame
        satd_df['type'] = df3['predicted_satd_type'].values



    return satd_df



# Add the type of the SATDs in the next columns. - done 
# Group the types of SATDs and sum them up.
# Combine a new csv file with community smells present in that release along with total number of SATDs and the predicted SATD types.


def grouping_SATD(df):
    # Map type numbers to readable labels
    SATD_LABELS = {
        0: 'Requirement',
        1: 'Code',
        2: 'M&T',
        3: 'Defect',
        4: 'Design',
        5: 'Documentation'
    }

    # Convert type to label
    df['type_label'] = df['type'].map(SATD_LABELS)

    # Total SATD per release
    total_satd = df.groupby('Version')['SATD'].sum().reset_index()
    total_satd = total_satd.rename(columns={'Version': 'Release'})

    # Count of each SATD type per release
    type_counts = df.groupby(['Version', 'type']).size().unstack(fill_value=0).reset_index()
    type_counts = type_counts.rename(columns={'Version': 'Release'})

    # Merge total + type counts
    result = pd.merge(total_satd, type_counts, on='Release')
    print(result)
    return result


def merge_community_smell_SATD(satd_df,repo):
    cs_df = pd.read_csv(f'csDetector-Result/{repo}_combined-result.csv')

    merged_df = cs_df.merge(satd_df, on="Release", how="left")

    smell_columns = ['OSE', 'BCE', 'PDE', 'SV', 'OS', 'SD', 'RS', 'TF', 'UI', 'TC']
    merged_df['CommunitySmells'] = merged_df[smell_columns].sum(axis=1)

    cols = merged_df.columns.tolist()
    tc_index = cols.index('TC')
    cols = cols[:tc_index+1] + ['CommunitySmells'] + cols[tc_index+1:-1]
    merged_df = merged_df[cols + ['SATD']]

    merged_df.to_csv(f'satd-datasets/{repo}_satd_type.csv', index=False)
    print('merged result to: ', f'satd-datasets/{repo}_satd_type.csv')
    return merged_df


if __name__ == "__main__":
    df = pd.read_csv('csDetector-Result/Repos-with-release.csv')
    for i, row in df.iterrows():
        # if i == 1: break
        owner = row['owner']
        repo = row['repo']
        
        GITHUB_REPO = owner + '/' + repo
      

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