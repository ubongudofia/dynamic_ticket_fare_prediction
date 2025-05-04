# import pandas as pd
# import json

# # Load your dataset (update path if needed)
# with open("utils/dynamic_railway_dataset.json", "r") as f:
#     data = json.load(f)

# # Convert to DataFrame
# df = pd.DataFrame(data)

# # Convert datetime fields
# df['departure_time'] = pd.to_datetime(df['departure_time'])
# df['departure_date'] = pd.to_datetime(df['departure_date'])

# # Feature engineering
# df['hour'] = df['departure_time'].dt.hour
# df['weekday'] = df['departure_date'].dt.day_name()

# # Select relevant features
# features = df[['train_name', 'departure', 'arrival', 'distance_km', 'hour', 'weekday', 'price']]

# # One-hot encode categorical columns
# features_encoded = pd.get_dummies(features, columns=['train_name', 'departure', 'arrival', 'weekday'])

# # Save to CSV for training
# features_encoded.to_csv("fare_prediction_training_data.csv", index=False)

# print("✅ Training dataset saved as fare_prediction_training_data.csv")




import pandas as pd
import json

# Load your dataset (update path if needed)
with open("utils/dynamic_railway_dataset.json", "r") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Convert datetime fields
df['departure_time'] = pd.to_datetime(df['departure_time'])
df['departure_date'] = pd.to_datetime(df['departure_date'])

# Feature engineering
df['hour'] = df['departure_time'].dt.hour
df['weekday'] = df['departure_date'].dt.day_name()
df['day_of_week'] = df['departure_date'].dt.dayofweek  # 0=Monday, ..., 6=Sunday

# Avoid division by zero in hour
df['distance_per_hour'] = df['distance_km'] / df['hour'].replace(0, 1)

# Weekend interaction: higher fare likelihood on weekends
df['hour_weekday_interaction'] = df['hour'] * df['weekday'].apply(lambda x: 1 if x in ['Saturday', 'Sunday'] else 0)

# Select relevant features (including target 'price')
features = df[['train_name', 'departure', 'arrival', 'distance_km', 'hour', 'weekday',
               'day_of_week', 'distance_per_hour', 'hour_weekday_interaction', 'price']]

# One-hot encode categorical columns
features_encoded = pd.get_dummies(features, columns=['train_name', 'departure', 'arrival', 'weekday'])

# Save to CSV for training
features_encoded.to_csv("fare_prediction_training_data_2.csv", index=False)

print("✅ Enhanced training dataset saved as fare_prediction_training_data.csv")
