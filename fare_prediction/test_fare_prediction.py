import joblib
import pandas as pd

# Load the trained model
model = joblib.load('fare_prediction/enhanced_linear_model.pkl')

# Example input
sample_input = {
    'distance_km': [20],
    'departure_hour': [8],
    'is_peak_hour': [1],
    'seat_availability_ratio': [0.9]
}

# Convert to DataFrame
sample_df = pd.DataFrame(sample_input)

# Calculate interaction terms (same as during training)
sample_df['distance_peak_interaction'] = sample_df['distance_km'] * sample_df['is_peak_hour']
sample_df['distance_demand_interaction'] = sample_df['distance_km'] * (1 - sample_df['seat_availability_ratio'])

# List of features (ensure the same features used in training are passed during prediction)
enhanced_features = ['distance_km', 'departure_hour', 'is_peak_hour', 'seat_availability_ratio', 
                     'distance_peak_interaction', 'distance_demand_interaction']

# Make prediction
predicted_fare = model.predict(sample_df[enhanced_features])

# Output the predicted fare
print(f"Predicted Fare: ₦{predicted_fare[0]:,.1f}")
