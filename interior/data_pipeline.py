"""
DESCRIPTION:
This script handles the exploratory data analysis, data cleaning, statistical feature extraction, 
and feature selection (using Correlation, Decision Trees, and PCA). It prepares and analyzes 
the raw data before formal model training begins.

INPUT:
Raw and partially cleaned CSV files (`train_file.csv`, `cleaned_data.csv`).

OUTPUT:
Cleaned datasets, a CSV of extracted statistical features (`statistical_features.csv`), 
and terminal/plot outputs visualizing feature importance and PCA variance.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ==========================================
# (A) UPLOADING OF DATA
# ==========================================
# Load your data
data_raw = pd.read_csv(r"D:\CS\AI\PROJECT\smart_home\train_file.csv")

# Drop Date and Time columns
data_raw = data_raw.drop(columns=['Date', 'Time'])

# ==========================================
# (B) CLEANING OF DATA
# ==========================================
# Load your cleaned data (Assuming it was saved previously or using the raw one)
data = pd.read_csv(r"D:\CS\AI\PROJECT\smart_home\cleaned_data.csv")

# Define your features (selecting relevant ones based on correlation)
selected_features = ['S1_Light','S3_Light' ,'S2_Light','S1_Temp','S7_PIR','S2_Temp','S5_CO2','S3_Temp','S6_PIR','S5_CO2_Slope','S1_Sound','S2_Sound','S3_Sound','S4_Temp','S4_Sound','S4_Light']

# Remove rows with missing values in the target variable
data = data.dropna(subset=['Room_Occupancy_Count'])

# Fill missing values with the mean (or median)
data['Room_Occupancy_Count'] = data['Room_Occupancy_Count'].fillna(data['Room_Occupancy_Count'].mean())

# Create X and y
X = data[selected_features]  # Select features
y = data['Room_Occupancy_Count']  # Target variable

# ==========================================
# (C) EXTRACTING THE STATISTICAL FEATURES
# ==========================================
# Define a function to extract statistical features
def extract_statistical_features(df):
    features = {}
    for column in df.columns[:-1]:  # Exclude the target variable
        features[f'{column}_mean'] = df[column].mean()
        features[f'{column}_median'] = df[column].median()
        features[f'{column}_std'] = df[column].std()
        features[f'{column}_min'] = df[column].min()
        features[f'{column}_max'] = df[column].max()
        features[f'{column}_skew'] = df[column].skew()
        features[f'{column}_kurt'] = df[column].kurtosis()
    return pd.Series(features)

# Apply feature extraction
statistical_features = extract_statistical_features(data)
print("Statistical Features:\n", statistical_features)

# Convert the extracted features to a DataFrame
statistical_features_df = statistical_features.to_frame(name='Value').reset_index()
statistical_features_df.columns = ['Feature', 'Value']

# Save to CSV
statistical_features_df.to_csv(r"D:\CS\AI\PROJECT\smart_home\statistical_features.csv", index=False)

# ==========================================
# (D) CORRELATION CALCULATION
# ==========================================
# Calculate the correlation matrix
correlation_matrix = data.corr()

# ==========================================
# (E) FEATURE SELECTION USING DECISION TREE
# ==========================================
# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and fit the Decision Tree model
dt_model = DecisionTreeRegressor(random_state=42)
dt_model.fit(X_train, y_train)

# Get feature importances
feature_importances = dt_model.feature_importances_

# Create a DataFrame for better visualization
importances_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': feature_importances
}).sort_values(by='Importance', ascending=False)

print("\nFeature Importances from Decision Tree:")
print(importances_df)

# ==========================================
# (E) FEATURE SELECTION USING PCA
# ==========================================
# Standardize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply PCA
pca = PCA()
pca.fit(X_scaled)

# Explained variance ratio
explained_variance = pca.explained_variance_ratio_

# Create a DataFrame for visualization
pca_df = pd.DataFrame({
    'Principal Component': range(1, len(explained_variance) + 1),
    'Variance Explained': explained_variance
})

print("\nExplained Variance by Principal Component:")
print(pca_df)

# Plotting the explained variance
plt.figure(figsize=(10, 6))
plt.plot(pca_df['Principal Component'], pca_df['Variance Explained'], marker='o')
plt.title('Explained Variance by Principal Component')
plt.xlabel('Principal Component')
plt.ylabel('Variance Explained')
plt.grid()
plt.show()

# Calculate cumulative explained variance
cumulative_variance = np.cumsum(explained_variance)

# Create a DataFrame for better visualization
cumulative_df = pd.DataFrame({
    'Principal Component': range(1, len(cumulative_variance) + 1),
    'Cumulative Variance': cumulative_variance
})

print("\nCumulative Variance:")
print(cumulative_df)
