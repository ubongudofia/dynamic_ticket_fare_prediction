import pandas as pd
import xgboost as xgb
from datetime import datetime




# https://chatgpt.com/share/6811359b-c680-8011-89a4-f919e7ee9287


# Load model and columns used during training
model = xgb.XGBRegressor()
model.load_model("fare_prediction_model.json")

# Load the training dataset to get column structure for encoding
training_df = pd.read_csv("fare_prediction_training_data.csv")
training_columns = training_df.drop(columns=["price"]).columns

# === INPUT: New Booking Data ===
new_data = {
    "train_name": "Express B",
    "departure": "Area One",
    "arrival": "Lugbe",
    "distance_km": 20,
    "departure_time": "2025-05-11 06:30:00",
    "departure_date": "2025-05-11",
}


# === FEATURE ENGINEERING ===
departure_time = pd.to_datetime(new_data["departure_time"])
departure_date = pd.to_datetime(new_data["departure_date"])

input_df = pd.DataFrame([{
    "train_name": new_data["train_name"],
    "departure": new_data["departure"],
    "arrival": new_data["arrival"],
    "distance_km": new_data["distance_km"],
    "hour": departure_time.hour,
    "weekday": departure_date.day_name()
}])

# === ONE-HOT ENCODE and ALIGN COLUMNS ===
input_encoded = pd.get_dummies(input_df)
# Ensure all expected columns are present
input_encoded = input_encoded.reindex(columns=training_columns, fill_value=0)

# === PREDICT FARE ===
predicted_fare = model.predict(input_encoded)[0]
print(f"💸 Predicted Fare: ₦{predicted_fare:.2f}")
