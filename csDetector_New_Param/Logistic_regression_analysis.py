import pandas as pd
import statsmodels.api as sm

# Create a DataFrame from the given data
data = {
    'Number of technical debt commits': [1164, 4331, 1308, 136, 271],
    'Number of commits SATD removed': [472, 3926, 1009, 118, 208],
    'Remaining percentage of commits': [94, 233, 595, 126, 234],
    'Total developer': [113, 1368, 160, 230, 585],
    'Days active': [4228, 6083, 6440, 4932, 8351],
    'Number of releases': [35, 98, 11, 54, 7],
    'Number of Community smell after SATD removal': [10, 12, 14, 16, 20]
}

df = pd.DataFrame(data)
df['Number of Community smell after SATD removal'] = df['Number of Community smell after SATD removal'].astype(int)
# Set up the logistic regression model
X = df[['Number of technical debt commits', 'Number of commits SATD removed', 'Remaining percentage of commits', 'Total developer', 'Days active', 'Number of releases']]
y = df['Number of Community smell after SATD removal']

# Add a constant term for the intercept
X = sm.add_constant(X)

# Fit the logistic regression model
model = sm.Logit(y, X).fit()

# Print the model summary
print(model.summary())
