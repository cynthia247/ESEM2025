import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load your correlation results
size = "large"  # or "medium"
df = pd.read_csv(f"satd-datasets/{size}_positive_correlations.csv")  # or full correlation file

# Option 1: Aggregate across all projects
heatmap_data = df.groupby(['CommunitySmell', 'SATD_Type'])['Correlation'].mean().unstack()

plt.figure(figsize=(10, 6))
sns.set_theme(font_scale=1.2)
sns.heatmap(heatmap_data, annot=True, cmap='BuPu', fmt=".2f")
plt.title(f"Average Correlation Between Community Smells and SATD Types in {size} Projects")
plt.xlabel("SATD Type")
plt.ylabel("Community Smell")
plt.tight_layout()
plt.savefig(f"satd-datasets/{size}_plot.png")


