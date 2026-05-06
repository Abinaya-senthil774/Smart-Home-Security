import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import pickle

# Load the cleaned data
data = pd.read_csv(r"D:\CS\AI\PROJECT\smart_home\cleaned_data.csv")

# Define your features
selected_features = ['S1_Light', 'S3_Light', 'S2_Light', 'S1_Temp', 'S7_PIR',
                    'S2_Temp', 'S5_CO2', 'S3_Temp', 'S6_PIR', 'S5_CO2_Slope',
                    'S1_Sound', 'S2_Sound', 'S3_Sound', 'S4_Temp', 'S4_Sound', 'S4_Light']

# Remove rows with missing values in the target variable
data = data.dropna(subset=['Room_Occupancy_Count'])
# Fill missing values in the target variable
data['Room_Occupancy_Count'] = data['Room_Occupancy_Count'].fillna(data['Room_Occupancy_Count'].mean())

# Create X and y
X = data[selected_features]
y = data['Room_Occupancy_Count']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train Logistic Regression model
log_reg = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
log_reg.fit(X_train_scaled, y_train)

# Evaluate the model
y_pred = log_reg.predict(scaler.transform(X_test))

# Print performance metrics
print("Logistic Regression Performance:")
print(classification_report(y_test, y_pred))
print(f"Accuracy: {accuracy_score(y_test, y_pred)}\n")

# Save the trained model and the scaler
with open('occupancy_model.pkl', 'wb') as model_file:
    pickle.dump(log_reg, model_file)

with open('scaler.pkl', 'wb') as scaler_file:
    pickle.dump(scaler, scaler_file)

print("Model and scaler saved as 'occupancy_model.pkl' and 'scaler.pkl'")

# Load the test data
test_data = pd.read_csv(r"D:\CS\AI\PROJECT\smart_home\test_file.csv")

# Ensure the test data has all necessary features
X_test = test_data[selected_features].copy()  # Select features based on training

# Handle missing values (if necessary)
X_test.fillna(X_test.mean(), inplace=True)

# Load the trained model and scaler
with open('occupancy_model.pkl', 'rb') as model_file:
    loaded_model = pickle.load(model_file)

with open('scaler.pkl', 'rb') as scaler_file:
    loaded_scaler = pickle.load(scaler_file)

# Scale the test data
X_test_scaled = loaded_scaler.transform(X_test)

# Make predictions
predictions = loaded_model.predict(X_test_scaled)

# Add predictions to the original test data
test_data['Predicted_Occupancy_Count'] = predictions

# Save the predictions to a new CSV file
test_data.to_csv('D:\CS\AI\PROJECT\smart_home\predicted_occupancy_counts.csv', index=False)

print("Predictions saved to 'D:\CS\AI\PROJECT\smart_home\predicted_occupancy_counts.csv'")

