import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the CSV result
df = pd.read_csv("mk_trend_summary2.csv", index_col=0)

# Create a separate DataFrame to extract numeric trend direction
def extract_direction(cell):
    if isinstance(cell, str):
        if "[↑]" in cell:
            return 1
        elif "[↓]" in cell:
            return -1
        elif "[–]" in cell:
            return 0
    return None

def extract_significance(cell):
    if isinstance(cell, str):
        if "***" in cell:
            return 3
        elif "**" in cell:
            return 2
        elif "*" in cell:
            return 1
    return 0

# Create numeric maps
direction_df = df.map(extract_direction)
significance_df = df.map(extract_significance)

# Combine both for coloring
# Value = direction * significance (e.g., ↑*** = 1 * 3 = 3, ↓** = -1 * 2 = -2)
heatmap_df = direction_df * significance_df

# Create a custom color palette
from matplotlib.colors import ListedColormap


colors = [
    "#d73027", "#f46d43", "#fdae61",  # decreasing: strong, medium, weak
    "#f0f0f0",                        # no trend
    "#bee3bd", "#9bd499", "#78c575"   # increasing: weak, medium, strong
]
cmap = ListedColormap([
    colors[0], colors[1], colors[2],  # -3, -2, -1
    colors[3],                        #  0
    colors[4], colors[5], colors[6]   # +1, +2, +3
])

# Create the heatmap
plt.figure(figsize=(20, 10))
sns.heatmap(
    heatmap_df,
    cmap=cmap,
    annot=df,
    fmt='',
    linewidths=0.5,
    linecolor='gray',
    cbar=False
)
plt.title("Mann-Kendall Trend Summary by Project", fontsize=16)
plt.xlabel("Project")
plt.ylabel("Smell / SATD Type")
plt.tight_layout()
plt.savefig("plot.png")
