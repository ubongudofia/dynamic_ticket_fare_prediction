import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# Load the data
df = pd.read_csv('fare_prediction/synthetic_fare_data.csv')

# Enhanced features
df['distance_peak_interaction'] = df['distance_km'] * df['is_peak_hour']
df['distance_demand_interaction'] = df['distance_km'] * (1 - df['seat_availability_ratio'])
enhanced_features = ['distance_km', 'departure_hour', 'is_peak_hour', 'seat_availability_ratio', 
                     'distance_peak_interaction', 'distance_demand_interaction']

# Target variable
target = 'final_fare'

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df[enhanced_features], df[target], test_size=0.2, random_state=42)

# Initialize the Linear Regression model
enhanced_model = LinearRegression()

# Train the model
enhanced_model.fit(X_train, y_train)

# Save the trained model
joblib.dump(enhanced_model, 'fare_prediction/enhanced_linear_model.pkl')

# Print out model performance on test data
y_pred = enhanced_model.predict(X_test)
rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
r2 = enhanced_model.score(X_test, y_test)

print(f"Model Performance on Test Data:")
print(f"RMSE: {rmse:.2f}")
print(f"R-squared: {r2:.4f}")

# Model saved successfully message
print("Enhanced Linear Model trained and saved as 'enhanced_linear_model.pkl'.")
