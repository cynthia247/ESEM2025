import pandas as pd
import statsmodels.api as sm
import numpy as np

# Sample data (you would replace this with your actual dataset)
data = {
    'Number of commits' : [2000, 5000, 3000, 800, 400],
    'Number of technical debt commits': [1164,	4331,	1317,	136	,271],
    # 'Number of commits SATD removed': [40.5,	90.6,	76.6,	87.9,	76.7],
    'Number of commits SATD removed': [472,	3926,	1009,	118,	208],
    # 'Remaining percentage of commits': [59.5,	9.4,	23.3,	12.6,	23.4],
    'Remaining percentage of commits': [692,	405,	308,	18,	64],
    'Total developer' : [313,	1368,	160,	230,	585],
    'Days active' : [4228,	6083,	6440	,4932,	8351],
    'Number of releases' : [35,	98	,11	,54	,7],
    'Number of Community smell before SATD removal': [7,	8,5,	7,	8],
    'Number of Community smell after SATD removal' : [2,2,3,2,2],
    'Number of SATD introduced developers' : [	64,	47,	19,	8,	28],
    'Number of SATD removal developers' :	[38,	37,	15,	7,	16]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Add a constant term for the intercept
df['Intercept'] = 1

# Define independent variables

df['log_td'] = np.log(df['Number of technical debt commits'])
df['log_SATDRemoved'] = np.log(df['Number of commits SATD removed'])
# df['log_percentage'] = np.log(df['Remaining percentage of commits'])
df['log_commits'] = np.log(df['Number of commits'])
df['log_beforeSATD'] = np.log(df['Number of Community smell before SATD removal'])
df['log_afterSATD'] = np.log(df['Number of Community smell after SATD removal'])
df['log_devintroSATD'] = np.log(df['Number of SATD introduced developers'])
df['log_devrmSATD'] = np.log(df['Number of SATD removal developers'])

X = df[[
        'Intercept', 
    'Number of technical debt commits', 
    # 'Number of commits SATD removed',
    # 'Intercept', 'log_commits' ,
    # 'log_td','log_SATDRemoved',
    'Number of SATD removal developers',
    'Total developer',
    # 'Days active'
    ]]
# Define the dependent variable
y = df['Number of SATD introduced developers']

# Fit the regression model
model = sm.OLS(y, X).fit()

# Print the summary
print(model.summary())


#Importing the libraries
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
# from sklearn import metrics
# # import seaborn as sns
# dataset = pd.read_csv("test.csv")
# x = dataset[[ 'Total developer','Days active','Number of releases','Number of Community smell before SATD removal','Number of Community smell after SATD removal']]
# y = dataset['Number of commits SATD removed']
# x_train, x_test, y_train, y_test= train_test_split(x, y, test_size= 0.3, random_state=100)
# mlr= LinearRegression()  
# mlr.fit(x_train, y_train) 

# #Printing the model coefficients
# print(mlr.intercept_)
# # pair the feature names with the coefficients
# print(list(zip(x, mlr.coef_)))

# #Predicting the Test and Train set result 
# y_pred_mlr= mlr.predict(x_test)  
# x_pred_mlr= mlr.predict(x_train) 

# print("Prediction for test set: {}".format(y_pred_mlr))
# mlr_diff = pd.DataFrame({'Actual value': y_test, 'Predicted value': y_pred_mlr})
# print(mlr_diff)
# print('R squared value of the model: {:.2f}'.format(mlr.score(x,y)*100))

# # 0 means the model is perfect. Therefore the value should be as close to 0 as possible
# meanAbErr = metrics.mean_absolute_error(y_test, y_pred_mlr)
# meanSqErr = metrics.mean_squared_error(y_test, y_pred_mlr)
# rootMeanSqErr = np.sqrt(metrics.mean_squared_error(y_test, y_pred_mlr))

# print('Mean Absolute Error:', meanAbErr)
# print('Mean Square Error:', meanSqErr)
# print('Root Mean Square Error:', rootMeanSqErr)