"""
DESCRIPTION:
This script scales the prepared features, evaluates multiple classification models 
(Logistic Regression, k-NN, Neural Network) for comparison, and finally trains and 
saves the ultimate Logistic Regression model and scaler to disk for deployment.

INPUT:
The cleaned dataset (`cleaned_data.csv`).

OUTPUT:
Performance metrics printed to the console (Classification Report, Accuracy, Confusion Matrix), 
feature importance plots, and exported pickle files (`occupancy_model.pkl` and `scaler.pkl`).
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

# Load the cleaned data
data = pd.read_csv(r"D:\CS\AI\PROJECT\smart_home\cleaned_data.csv")

# Define features and target
selected_features = ['S1_Light', 'S3_Light', 'S2_Light', 'S1_Temp', 'S7_PIR',
                    'S2_Temp', 'S5_CO2', 'S3_Temp', 'S6_PIR', 'S5_CO2_Slope',
                    'S1_Sound', 'S2_Sound', 'S3_Sound', 'S4_Temp', 'S4_Sound', 'S4_Light']

# Remove rows with missing values in the target variable
data = data.dropna(subset=['Room_Occupancy_Count'])
data['Room_Occupancy_Count'] = data['Room_Occupancy_Count'].fillna(data['Room_Occupancy_Count'].mean())

features = data.drop(columns=['Room_Occupancy_Count'])
target = data['Room_Occupancy_Count']
X = data[selected_features]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================================
# (F) LOGISTIC REGRESSION ANALYSIS
# ==========================================
model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)
predictions = model.predict(X_test_scaled)

# Coefficients and feature importance
coefficients = pd.DataFrame(model.coef_[0], index=features.columns, columns=['Coefficient'])

# Plotting feature importance
plt.figure(figsize=(12, 6))
sns.barplot(x=coefficients['Coefficient'], y=coefficients.index)
plt.title('Feature Importances from Logistic Regression')
plt.xlabel('Coefficient Value')
plt.ylabel('Feature')
plt.axvline(0, color='grey', linestyle='--')
plt.show()

# ==========================================
# (G) MULTI CLASS CLASSIFICATION METHODS
# ==========================================
# Train-test split specifically for X containing selected_features
X_train_sel, X_test_sel, y_train_sel, y_test_sel = train_test_split(X, target, test_size=0.2, random_state=42)

scaler_sel = StandardScaler()
X_train_scaled_sel = scaler_sel.fit_transform(X_train_sel)
X_test_scaled_sel = scaler_sel.transform(X_test_sel)

# Logistic Regression
log_reg = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
log_reg.fit(X_train_scaled_sel, y_train_sel)
log_reg_pred = log_reg.predict(X_test_scaled_sel)

# k-NN
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled_sel, y_train_sel)
knn_pred = knn.predict(X_test_scaled_sel)

# Neural Network
nn = MLPClassifier(hidden_layer_sizes=(10,), max_iter=1000)
nn.fit(X_train_scaled_sel, y_train_sel)
nn_pred = nn.predict(X_test_scaled_sel)

# Evaluation
models = {
    "Logistic Regression": log_reg_pred,
    "k-NN": knn_pred,
    "Neural Network": nn_pred
}

print("\n--- MODEL COMPARISON ---")
for model_name, preds in models.items():
    print(f"\n{model_name} Performance:")
    print(classification_report(y_test_sel, preds))
    print(f"Accuracy: {accuracy_score(y_test_sel, preds)}")
    print(f"Confusion Matrix:\n{confusion_matrix(y_test_sel, preds)}\n")

# ==========================================
# (H) FINAL MODEL TRAINING & SAVING
# ==========================================
# Save the trained Logistic Regression model and the scaler
with open('occupancy_model.pkl', 'wb') as model_file:
    pickle.dump(log_reg, model_file)

with open('scaler.pkl', 'wb') as scaler_file:
    pickle.dump(scaler_sel, scaler_file)

print("Final Model and scaler saved as 'occupancy_model.pkl' and 'scaler.pkl'")
