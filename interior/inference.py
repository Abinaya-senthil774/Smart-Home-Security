"""
DESCRIPTION:
This script simulates real-time deployment (or batch testing) by loading 
the saved machine learning model and scaler, reading unseen test data, 
and outputting occupancy predictions.

INPUT:
The saved model files (`occupancy_model.pkl`, `scaler.pkl`) and a 
test dataset (`test_file.csv`).

OUTPUT:
A new CSV file (`predicted_occupancy_counts.csv`) containing the original 
test data appended with a 'Predicted_Occupancy_Count' column.
"""

import pandas as pd
import pickle

# Define the features the model was trained on
selected_features = ['S1_Light', 'S3_Light', 'S2_Light', 'S1_Temp', 'S7_PIR',
                    'S2_Temp', 'S5_CO2', 'S3_Temp', 'S6_PIR', 'S5_CO2_Slope',
                    'S1_Sound', 'S2_Sound', 'S3_Sound', 'S4_Temp', 'S4_Sound', 'S4_Light']

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

# Scale the test data using the saved scaler
X_test_scaled = loaded_scaler.transform(X_test)

# Make predictions
predictions = loaded_model.predict(X_test_scaled)

# Add predictions to the original test data
test_data['Predicted_Occupancy_Count'] = predictions

# Save the predictions to a new CSV file
output_path = r"D:\CS\AI\PROJECT\smart_home\predicted_occupancy_counts.csv"
test_data.to_csv(output_path, index=False)

print(f"Predictions successfully saved to '{output_path}'")
