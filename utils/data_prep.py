import pandas as pd
from datetime import datetime

def preprocess_fare_data(filepath):
    # Load data
    df = pd.read_json(filepath)

    # Convert to datetime
    df["departure_time"] = pd.to_datetime(df["departure_time"])

    # Feature Engineering
    df["departure_hour"] = df["departure_time"].dt.hour
    df["day_of_week"] = df["departure_time"].dt.dayofweek  # Monday = 0
    df["is_peak_hour"] = df["departure_hour"].apply(lambda x: 1 if 7 <= x <= 9 or 17 <= x <= 19 else 0)

    return df

if __name__ == "__main__":
    # Replace with your path to JSON file
    filepath = "dynamic_railway_dataset.json"
    df = preprocess_fare_data(filepath)

    # Show transformed features
    print(df[["route_name", "train_name", "departure_hour", "day_of_week", "is_peak_hour", "distance_km", "price"]])
