# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt

# # Load your correlation results
# df = pd.read_csv("satd-datasets/large_positive_correlations.csv")  # or full correlation file

# # Option 1: Aggregate across all projects
# heatmap_data = df.groupby(['CommunitySmell', 'SATD_Type'])['Correlation'].mean().unstack()

# plt.figure(figsize=(10, 6))
# sns.heatmap(heatmap_data, annot=True, cmap='Reds', fmt=".2f")
# plt.title("Average Correlation Between Community Smells and SATD Types")
# plt.xlabel("SATD Type")
# plt.ylabel("Community Smell")
# plt.tight_layout()
# plt.savefig("plot.png")



import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load your data (replace 'your_results.csv' with your actual file)
data = pd.read_csv('satd-datasets/small_positive_correlations.csv')  # Example: 'results.csv'

# Filter for significant results (p < 0.05)
significant_data = data[data['P_Value'] < 0.05]

# Get unique projects
projects = significant_data['Project'].unique()

# Loop through each project and create a separate bar plot
for project in projects:
    # Filter data for the current project
    project_data = significant_data[significant_data['Project'] == project]
    
    # Create the plot
    plt.figure(figsize=(10, 6))  # Adjust size as needed
    sns.barplot(data=project_data, x='CommunitySmell', y='Correlation', hue='SATD_Type', dodge=True)
    
    # Customize the plot
    plt.axhline(0, color='gray', linestyle='--')  # Add zero line for reference
    plt.title(f'Correlation between Community Smells and SATD Types in {project}', fontsize=12)
    plt.xlabel('Community Smell', fontsize=10)
    plt.ylabel('Spearman ρ', fontsize=10)
    plt.legend(title='SATD Type', title_fontsize=10, fontsize=9)
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
    
    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # Save the plot (optional)
    plt.savefig("plot.png", dpi=300, bbox_inches='tight')
    
    # Show the plot (comment out if saving only)
    plt.show()
    
    # Close the figure to free memory
    plt.close()

print("Plots generated for all projects.")