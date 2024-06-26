# -*- coding: utf-8 -*-
"""Long_Short-Term_Memory_Network_ipynb(Complete).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EgmsX5Zrq1o-nZOGIxTelwKWpFFcWlBR

###Long Short-Term Network

### Importing the libraries
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import tensorflow as tf

tf.__version__

"""## Data Preprocessing

### Importing the dataset
"""

dataset = pd.read_csv('/content/Churn_Modelling.csv')

dataset.sample(5)

dataset.shape

"""# Data Cleaning

"""

dataset.drop('RowNumber' ,axis='columns',inplace=True)

dataset

dataset.drop('CustomerId' ,axis='columns',inplace=True)
dataset.drop('Surname' ,axis='columns',inplace=True)

dataset.sample(5)

Ext_N0 = dataset[dataset.Exited==0].Tenure
Ext_YES = dataset[dataset.Exited==1].Tenure

plt.xlabel('Tenure')
plt.ylabel('No. of customers')
plt.title('Customer Prediction')
plt.hist([Ext_N0,Ext_YES], color=['green','red'],label=['Exited=No','Exited=Yes'])
plt.legend()

"""### Encoding categorical data

Label Encoding the "Gender" column
"""

dataset['Gender'].replace({'Female':1, 'Male':0},inplace=True)

dataset.sample(2)

"""###Split Data"""

#Dependent Var is Y
#Independent Var is X
X = dataset.iloc[:,:-1]

X

Y = dataset.iloc[:,-1]

Y

"""One Hot Encoding the "Geography" column"""

one_hot = pd.get_dummies(dataset['Geography'], drop_first=False).astype(int)

one_hot

dataset

dataset=dataset.drop('Geography',axis=1)

dataset

dataset = dataset.join(one_hot)

dataset

X

Y

"""###Spliting the dataset into features (X) and target (Y)"""

# Split the dataset into features (X) and target (Y)
X = dataset.drop('Exited', axis=1)
Y = dataset['Exited']

X

Y

"""###Handling Imbalanced Data"""

# Calculate the IQR for each feature
Q1 = dataset.quantile(0.25)
Q3 = dataset.quantile(0.75)
IQR = Q3 - Q1

# Define the lower and upper bounds for outlier detection
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
# Remove outliers
dataset = dataset[~((dataset < lower_bound) | (dataset > upper_bound))].dropna()

# Print the updated dataset
print(dataset)
print(dataset.head())

from imblearn.combine import SMOTEENN

# Apply SMOTEENN (SMOTE + Edited Nearest Neighbors) to balance the classes
smoteenn = SMOTEENN()
X_sm, Y_sm = smoteenn.fit_resample(X, Y)

"""###Checking for Outliers"""

from scipy import stats

# List of columns to check for outliers
columns = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary']

# For each column, calculate the z-scores and print the number of outliers
for col in columns:
    z_scores = np.abs(stats.zscore(dataset[col]))
    outliers = z_scores > 3
    print(f"{col} has {outliers.sum()} outliers")

"""### Removing Outliers from 'Age' Column Using IQR"""

Q1 = dataset['Age'].quantile(0.25)
Q3 = dataset['Age'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

from scipy import stats

# List of columns to check for outliers
columns = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary']

# For each column, calculate the z-scores and print the number of outliers
for col in columns:
    z_scores = np.abs(stats.zscore(dataset[col]))
    outliers = z_scores > 3
    print(f"{col} has {outliers.sum()} outliers")

# Remove outliers
dataset = dataset[(dataset['Age'] >= lower_bound) & (dataset['Age'] <= upper_bound)]

# Print the updated dataset shape
print(f"Dataset shape after removing outliers: {dataset.shape}")

"""###Checking for Outliers in 'Age' Column Again"""

z_scores = np.abs(stats.zscore(dataset['Age']))
outliers = z_scores > 3
print(f"Age column has {outliers.sum()} outliers after removal")

"""###Checking for data balance


"""

# Check Class Distribution before Balancing
class_counts = Y.value_counts()
print("Class distribution before balancing:")
print(class_counts)

# Check Class Distribution After Balancing
class_counts_sm = Y_sm.value_counts()
print("Class distribution after balancing:")
print(class_counts_sm)

ratio_sm = class_counts_sm[1] / class_counts_sm[0]
print(f"Ratio of class 1 to class 0 after balancing: {ratio_sm:.2f}")

"""### Splitting the dataset into Training and Testing set"""

from sklearn.model_selection import train_test_split
X_sm_train, X_sm_test, Y_sm_train, Y_sm_test = train_test_split(X_sm, Y_sm, test_size = 0.2, random_state = 0)

X_sm_train

X_sm_test

from sklearn.preprocessing import RobustScaler

# Create a scaler object
scaler = RobustScaler()

# Fit and transform the data
X_train_scaled = scaler.fit_transform(X_sm_train)
X_test_scaled = scaler.transform(X_sm_test)

"""### Using Grid Search algorithm to find the best parameters to build our RNN model"""

# Function to create model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
def create_model():
    lstm_model = Sequential()
    lstm_model.add(LSTM(units=64, activation='relu', input_shape=(1, X_train_scaled.shape[1])))
    lstm_model.add(Dropout(0.2))
    lstm_model.add(Dense(units=32, activation='relu'))
    lstm_model.add(Dropout(0.2))

    lstm_model.add(Dense(units=1, activation='sigmoid'))
    return lstm_model



from sklearn.base import BaseEstimator, ClassifierMixin
# Custom KerasClassifier class
class KerasClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, create_model_fn, batch_size=32, epochs=100):
        self.create_model_fn = create_model_fn
        self.batch_size = batch_size
        self.epochs = epochs
        self.model = None

    def fit(self, X_train_scaled, Y_sm_train):
        self.model = self.create_model_fn()
        self.model.fit(X_train_scaled, Y_sm_train, batch_size=self.batch_size, epochs=self.epochs)
        return self

    def predict(self, X_train_scaled):
        return (self.model.predict(X_train_scaled) > 0.5).astype(int)

# Create a KerasClassifier
model = KerasClassifier(create_model)

from sklearn.model_selection import train_test_split, GridSearchCV


# Define the grid search parameters
param_grid = {
    'batch_size': [6, 12, 32, 64],
    'epochs': [50, 100, 150, 200]
}

# Perform grid search
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, scoring='accuracy', cv=3)
grid_result = grid_search.fit(X_train_scaled, Y_sm_train)

# Print the best parameters and score
print("Best parameters: ", grid_result.best_params_)
print("Best score: ", grid_result.best_score_)

# Reshape the data for LSTM models
X_train_rnn = np.reshape(X_train_scaled, (X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
X_test_rnn = np.reshape(X_test_scaled, (X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))

# Import the necessary module
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense

# Define the LSTM model
lstm_model = Sequential()
lstm_model.add(LSTM(units=64, activation='relu', input_shape=(1, X_train_scaled.shape[1])))
lstm_model.add(Dropout(0.2))
lstm_model.add(Dense(units=32, activation='relu'))
lstm_model.add(Dropout(0.2))

lstm_model.add(Dense(units=1, activation='sigmoid'))

# Compile the LSTM model
lstm_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the LSTM model
lstm_history = lstm_model.fit(X_train_rnn, Y_sm_train, validation_data=(X_test_rnn, Y_sm_test), epochs=50, batch_size=64)

"""###Building the LSTM model with best parameters

### Making predictions from the model
"""

Y_pred = lstm_model.predict(X_test_rnn)
Y_pred = (Y_pred > 0.5)
print(np.concatenate((Y_pred.reshape(len(Y_pred),1), np.array(Y_sm_test).reshape(len(Y_sm_test),1)),1))

print(Y_pred)

"""##Predicting the result of a single observation

Using our ANN model to predict if the customer with the following informations will leave the bank:

    1.Geography: France
    2.Credit Score: 600
    3.Gender: Male
    4.Age: 40 years old
    5.Tenure: 3 years
    6.Balance: $ 60000
    7.Number of Products: 2
    8.Does this customer have a credit card? Yes
    9.Is this customer an Active Member: Yes
    10.Estimated Salary: $ 50000
"""

import numpy as np
import pandas as pd

# Assuming 'scaler' is your RobustScaler and 'features' is a list of feature names
features = [ 'CreditScore', 'Gender', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 'France', 'Germany', 'Spain']

# Create a DataFrame with the correct feature names
X = pd.DataFrame([[600, 1, 40, 3, 60000, 2, 1, 1, 50000, 1, 0, 0]], columns=features)

# Use the scaler to transform the data
X_test_rnn = scaler.transform(X)

# Reshape the data to match the RNN model's input shape
X_test_rnn = np.reshape(X_test_rnn, (X_test_rnn.shape[0], 1, X_test_rnn.shape[1]))

# Use the LSTM to predict the transformed data
print(lstm_model.predict(X_test_rnn) )

"""###Evaluating the model using various metrics"""

from sklearn.metrics import precision_score, recall_score, accuracy_score

# Calculate precision
precision = precision_score(Y_sm_test, Y_pred)
print("Precision:", precision)

# Calculate recall
recall = recall_score(Y_sm_test, Y_pred)
print("Recall:", recall)

# Calculate accuracy
accuracy = accuracy_score(Y_sm_test, Y_pred)
print("Accuracy:", accuracy)

from sklearn.metrics import f1_score
f1 = f1_score(Y_sm_test, Y_pred)
print("F1 Score:", f1)

"""### Making the Confusion Matrix and Heatmap"""

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

# Create confusion matrix
cm = confusion_matrix(Y_sm_test, Y_pred)
print(cm)

# Create heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.title('Confusion matrix')
plt.show()

"""###Heatmap for accuracy,precision, recall, f1 score"""

# Calculate confusion matrix
cm = confusion_matrix(Y_sm_test, Y_pred)
print(cm)

# Calculate metrics for each class
accuracy_0 = cm[0, 0] / (cm[0, 0] + cm[0, 1])
accuracy_1 = cm[1, 1] / (cm[1, 0] + cm[1, 1])
precision_0 = precision_score(Y_sm_test, Y_pred, pos_label=0)
precision_1 = precision_score(Y_sm_test, Y_pred, pos_label=1)
recall_0 = recall_score(Y_sm_test, Y_pred, pos_label=0)
recall_1 = recall_score(Y_sm_test, Y_pred, pos_label=1)
f1_0 = f1_score(Y_sm_test, Y_pred, pos_label=0)
f1_1 = f1_score(Y_sm_test, Y_pred, pos_label=1)

# Create a dictionary with the metrics
metrics = {
    'Accuracy': [accuracy_0, accuracy_1],
    'Precision': [precision_0, precision_1],
    'Recall': [recall_0, recall_1],
    'F1 Score': [f1_0, f1_1]
}

# Convert the dictionary to a DataFrame for easier plotting
metrics_df = pd.DataFrame(metrics, index=['Class 0', 'Class 1'])

# Set up the figure
plt.figure(figsize=(12, 6))

# Define a color palette
cmap = sns.diverging_palette(220, 20, as_cmap=True)

# Create the heatmap
sns.heatmap(metrics_df, annot=True, cmap=cmap, cbar=True, fmt='.2f', annot_kws={"size": 14}, linewidths=2, linecolor='white')

# Customize the aesthetics
plt.title('Model Evaluation Metrics Heatmap for Each Class', fontsize=18, fontweight='bold', color='darkblue', pad=20)
plt.xlabel('Metrics', fontsize=14, labelpad=10)
plt.ylabel('Class', fontsize=14, labelpad=10)
plt.xticks(fontsize=12, rotation=0)
plt.yticks(fontsize=12, rotation=0)

# Show the heatmap
plt.tight_layout()
plt.show()

"""###Loss vs Accuracy"""

# Plotting Loss and accuracy
plt.plot(lstm_history.history['loss'], label='Loss')
plt.plot(lstm_history.history['accuracy'], label='Accuracy')
plt.title('Loss and Accuracy')
plt.ylabel('Loss')
plt.xlabel('Accuracy')
plt.legend()
plt.show()