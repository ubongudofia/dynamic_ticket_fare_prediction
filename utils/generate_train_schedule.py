from pymongo import MongoClient
import certifi
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone, timedelta
import random
from bson.objectid import ObjectId
import os
import json


# MongoDB connection string
mongo_client = "mongodb://localhost:27017/e_ticketing"

try:
    # Connect to MongoDB with SSL certification
    client = MongoClient(mongo_client)  # Use MongoClient correctly

    # Get the database
    db = client.get_database("e_ticketing")

    # Check if connection is successful by listing collections
    collections = db.list_collection_names()

    print("✅ Successfully connected to MongoDB!")
    print("Collections in 'e_ticketing':", collections)
except Exception as e:
    print("❌ Error connecting to MongoDB:", e)



# ======================== CREATE TRAIN SCHEDULES STRATS HERE ========================

# Collection storing train schedules

db = client["e_ticketing"]
train_schedules_collection = db["train_schedules"]

# List of active train IDs
train_ids = [
    ObjectId("67d4e81a61abe421d4140d5f"),  # Express A
    ObjectId("67d4e81a61abe421d4140d60"),  # Metro A
    ObjectId("67d4e81a61abe421d4140d61"),  # Express B
    ObjectId("67d4e81a61abe421d4140d62")   # Metro B
]

# List of route IDs
route_ids = [
    ObjectId("67ea86762405e78f49b1d81c"),  # ABJ TOWN EXPRESS - LUB/AREA1
    ObjectId("67ea86762405e78f49b1d81d"),  # ABJ TOWN EXPRESS - LUB/NYA
    ObjectId("67ea86762405e78f49b1d81e"),  # ABJ TOWN EXPRESS - AREA1/LUB
    ObjectId("67ea86762405e78f49b1d81f"),  # ABJ TOWN EXPRESS - AREA1/NYA
    ObjectId("67ea86762405e78f49b1d820"),  # ABJ TOWN EXPRESS - NYA/LUB
    ObjectId("67ea86762405e78f49b1d821")   # ABJ TOWN EXPRESS - NYA/AREA1
]

# Starting date for scheduling
start_date = datetime.strptime("2025-05-01", "%Y-%m-%d")

# Schedule generation for the next 5 days
for train_id in train_ids:
    for route_id in route_ids:
        for i in range(5):  # Generate schedules for the next 5 days
            # Calculate the schedule date
            schedule_date = start_date + timedelta(days=i)
            departure_time = (8 + i) % 24  # Randomize departure time (for example, 08:30, 09:30, etc.)
            departure_time_str = f"{departure_time:02}:30"  # Format to HH:30

            # Correct the arrival time calculation
            departure_hour = int(departure_time_str[:2])  # Convert the hour part to an integer
            arrival_hour = (departure_hour + 1) % 24  # Add 1 hour to the departure hour, wrapping around if necessary
            arrival_time = f"{arrival_hour:02}:00"  # Format to HH:00

            # Generate a schedule for each train-route pair on a specific date
            schedule = {
                "train_id": train_id,
                "route_id": route_id,
                "departure_time": departure_time_str,
                "arrival_time": arrival_time,
                "departure_date": schedule_date.strftime("%Y-%m-%d"),
                "available_seats": [
                    {"seat_number": f"A{i+1}", "status": "available"} for i in range(10)
                ],
                "status": "Scheduled"
            }

            # Insert the schedule into the train_schedules collection
            result = train_schedules_collection.insert_one(schedule)
            print(f"Train schedule inserted for train {train_id} on route {route_id} for date {schedule_date.strftime('%Y-%m-%d')} with ID: {result.inserted_id}")


# ======================== CREATE TRAIN SCHEDULES ENDS HERE ========================

