import random
import json
from datetime import datetime, timedelta
import pytz

# Mock data for generating synthetic bookings
routes = [
    {"_id": "67ea86762405e78f49b1d81e", "route_name": "ABJ TOWN EXPRESS - AREA1/LUB", "departure": "Area One", "arrival": "Lugbe", "distance_km": 20, "base_rate": 1500},
    {"_id": "67ea86762405e78f49b1d820", "route_name": "ABJ TOWN EXPRESS - NYA/LUB", "departure": "Nyanya", "arrival": "Lugbe", "distance_km": 30, "base_rate": 1500},
    {"_id": "67ea86762405e78f49b1d821", "route_name": "ABJ TOWN EXPRESS - NYA/AREA1", "departure": "Nyanya", "arrival": "Area One", "distance_km": 15, "base_rate": 1500},
    {"_id": "67ea86762405e78f49b1d81c", "route_name": "ABJ TOWN EXPRESS - LUB/AREA1", "departure": "Lugbe", "arrival": "Area One", "distance_km": 20, "base_rate": 1500},
    {"_id": "67ea86762405e78f49b1d81d", "route_name": "ABJ TOWN EXPRESS - LUB/NYA", "departure": "Lugbe", "arrival": "Nyanya", "distance_km": 30, "base_rate": 1500},
    {"_id": "67ea86762405e78f49b1d81f", "route_name": "ABJ TOWN EXPRESS - AREA1/NYA", "departure": "Area One", "arrival": "Nyanya", "distance_km": 15, "base_rate": 1500}
]

trains = [
    {"_id": "67d4e81a61abe421d4140d5f", "train_name": "Express A", "train_number": "101", "capacity": 10},
    {"_id": "67d4e81a61abe421d4140d62", "train_name": "Metro B", "train_number": "104", "capacity": 10},
    {"_id": "67d4e81a61abe421d4140d60", "train_name": "Metro A", "train_number": "102", "capacity": 10},
    {"_id": "67d4e81a61abe421d4140d61", "train_name": "Express B", "train_number": "103", "capacity": 10}
]

# Calculate synthetic fare based on availability, peak hours, and distance
def calculate_synthetic_fare(route, departure_time, available_seats, total_seats):
    """
    Calculate the fare based on seat availability, peak hours, and distance.
    """
    base_rate = route["base_rate"]
    distance_km = route["distance_km"]
    
    # Distance multiplier (5% per km)
    distance_multiplier = 1 + (0.05 * distance_km)

    # Peak hours calculation based on departure_time
    nigeria_time = pytz.timezone("Africa/Lagos")
    departure_time_local = departure_time.astimezone(nigeria_time)
    departure_hour = departure_time_local.hour
    peak_factor = 1.2 if (7 <= departure_hour <= 9 or 17 <= departure_hour <= 19) else 1.0

    # Demand factor calculation based on seat availability
    seat_availability_ratio = available_seats / total_seats
    
    if seat_availability_ratio > 0.7:
        demand_factor = 1.0  # Normal price (70-100% seats available)
    elif seat_availability_ratio > 0.3:
        demand_factor = 1.2  # Medium demand (30-70% available)
    else:
        demand_factor = 1.5  # High demand (<30% available)

    # Final fare calculation
    final_fare = base_rate * distance_multiplier * peak_factor * demand_factor

    return round(final_fare, 2)

# Generate synthetic booking data
def generate_booking_data():
    route = random.choice(routes)
    train = random.choice(trains)

    # Generate random departure date within the next 100 days
    today = datetime.today()
    departure_date = today + timedelta(days=random.randint(1, 100))

    # Generate departure time at :30 for alignment with train schedule
    departure_time = datetime.combine(departure_date, datetime.min.time()) + timedelta(hours=random.randint(6, 20), minutes=30)

    # Generate seat number (assuming 10 seats per train)
    seat_number = f"A{random.randint(1, 10)}"

    # Calculate price dynamically using seat availability
    base_rate = route["base_rate"]
    total_seats = 10  # Assuming each train has 10 seats
    available_seats = random.randint(1, total_seats)  # Random available seats

    price = calculate_synthetic_fare(route, departure_time, available_seats, total_seats)

    return {
        "route_name": route["route_name"],
        "train_name": train["train_name"],
        "departure": route["departure"],
        "arrival": route["arrival"],
        "seat_number": seat_number,
        "price": round(price),
        "departure_time": departure_time.strftime("%Y-%m-%d %H:%M:%S"),
        "departure_date": departure_date.strftime("%Y-%m-%d"),
        "distance_km": route["distance_km"]
    }

def generate_synthetic_data(num_records):
    data = [generate_booking_data() for _ in range(num_records)]
    return data

# Generate 5000 synthetic booking records
synthetic_data = generate_synthetic_data(5000)

# Save to JSON file
with open("updated_3_synthetic_bookings.json", "w") as file:
    json.dump(synthetic_data, file, indent=4)

print("Synthetic data generated and saved to synthetic_bookings.json.")































# import json

# # Load the existing dataset
# with open("updated_synthetic_bookings_with_distance.json", "r") as file:
#     data = json.load(file)

# # Define train capacity mapping
# trains = [
#     {"_id": "67d4e81a61abe421d4140d5f", "train_name": "Express A", "train_number": "101", "capacity": 10},
#     {"_id": "67d4e81a61abe421d4140d62", "train_name": "Metro B", "train_number": "104", "capacity": 10},
#     {"_id": "67d4e81a61abe421d4140d60", "train_name": "Metro A", "train_number": "102", "capacity": 10},
#     {"_id": "67d4e81a61abe421d4140d61", "train_name": "Express B", "train_number": "103", "capacity": 10}
# ]

# # Create a dictionary for quick lookup
# train_capacity_map = {train["_id"]: train["capacity"] for train in trains}

# # Add capacity to each booking record
# for record in data:
#     record["capacity"] = train_capacity_map.get(record["train_id"], None)  # Add capacity if train_id exists

# # Save the updated dataset
# with open("updated_synthetic_bookings_with_capacity.json", "w") as file:
#     json.dump(data, file, indent=4)

# print("Dataset updated successfully! Check 'updated_synthetic_bookings_with_capacity.json'.")















# ===============================================================================================


# import random
# import json
# from datetime import datetime, timedelta
# import pytz

# # Mock data for generating synthetic bookings
# routes = [
#     {"_id": "67ea86762405e78f49b1d81e", "route_name": "ABJ TOWN EXPRESS - AREA1/LUB", "departure": "Area One", "arrival": "Lugbe", "distance_km": 20, "base_rate": 1500},
#     {"_id": "67ea86762405e78f49b1d820", "route_name": "ABJ TOWN EXPRESS - NYA/LUB", "departure": "Nyanya", "arrival": "Lugbe", "distance_km": 30, "base_rate": 1500},
#     {"_id": "67ea86762405e78f49b1d821", "route_name": "ABJ TOWN EXPRESS - NYA/AREA1", "departure": "Nyanya", "arrival": "Area One", "distance_km": 15, "base_rate": 1500},
#     {"_id": "67ea86762405e78f49b1d81c", "route_name": "ABJ TOWN EXPRESS - LUB/AREA1", "departure": "Lugbe", "arrival": "Area One", "distance_km": 20, "base_rate": 1500},
#     {"_id": "67ea86762405e78f49b1d81d", "route_name": "ABJ TOWN EXPRESS - LUB/NYA", "departure": "Lugbe", "arrival": "Nyanya", "distance_km": 30, "base_rate": 1500},
#     {"_id": "67ea86762405e78f49b1d81f", "route_name": "ABJ TOWN EXPRESS - AREA1/NYA", "departure": "Area One", "arrival": "Nyanya", "distance_km": 15, "base_rate": 1500}
# ]

# trains = [
#     {"_id": "67d4e81a61abe421d4140d5f", "train_name": "Express A", "train_number": "101", "capacity": 10},
#     {"_id": "67d4e81a61abe421d4140d62", "train_name": "Metro B", "train_number": "104", "capacity": 10},
#     {"_id": "67d4e81a61abe421d4140d60", "train_name": "Metro A", "train_number": "102", "capacity": 10},
#     {"_id": "67d4e81a61abe421d4140d61", "train_name": "Express B", "train_number": "103", "capacity": 10}
# ]

# # Generate synthetic booking data
# def generate_booking_data():
#     route = random.choice(routes)
#     train = random.choice(trains)

#     # Generate random departure date within the next 30 days
#     today = datetime.today()
#     departure_date = today + timedelta(days=random.randint(1, 30))

#     # Generate departure time within a time window (e.g., between 6 AM and 8 PM)
#     departure_time = datetime.combine(departure_date, datetime.min.time()) + timedelta(hours=random.randint(6, 20), minutes=random.randint(0, 59))

#     # Generate seat number (assuming 10 seats per train)
#     seat_number = f"A{random.randint(1, 10)}"

#     # Calculate price (base rate + dynamic adjustments like distance, peak hours, and demand)
#     base_rate = route["base_rate"]
#     distance_multiplier = 1 + (0.05 * route["distance_km"])  # 5% per km
#     peak_factor = 1.2 if (6 <= departure_time.hour <= 9 or 17 <= departure_time.hour <= 19) else 1.0  # Peak hours: 6-9 AM, 5-7 PM
#     demand_factor = 1.5 if random.random() < 0.3 else 1.0  # 30% chance for higher demand

#     price = base_rate * distance_multiplier * peak_factor * demand_factor

#     return {
#         "route_id": route["_id"],
#         "train_id": train["_id"],
#         "departure": route["departure"],
#         "arrival": route["arrival"],
#         "seat_number": seat_number,
#         "price": round(price, 2),
#         "departure_time": departure_time.strftime("%Y-%m-%d %H:%M:%S"),
#         "departure_date": departure_date.strftime("%Y-%m-%d")
#     }

# def generate_synthetic_data(num_records):
#     data = [generate_booking_data() for _ in range(num_records)]
#     return data

# # Generate 5000 synthetic booking records
# synthetic_data = generate_synthetic_data(5000)

# # Save to JSON file
# with open("updated_2_synthetic_bookings.json", "w") as file:
#     json.dump(synthetic_data, file, indent=4)

# print("Synthetic data generated and saved to synthetic_bookings.json.")




# ====================================================================================




















# # import random
# # from datetime import datetime, timedelta
# # import pytz
# # import json
# # import os

# # # Mock data for generating synthetic bookings
# # routes = [
# #     {"_id": "67ea86762405e78f49b1d81e", "route_name": "ABJ TOWN EXPRESS - AREA1/LUB", "departure": "Area One", "arrival": "Lugbe", "distance_km": 20, "base_rate": 1500},
# #     {"_id": "67ea86762405e78f49b1d820", "route_name": "ABJ TOWN EXPRESS - NYA/LUB", "departure": "Nyanya", "arrival": "Lugbe", "distance_km": 30, "base_rate": 1500},
# #     {"_id": "67ea86762405e78f49b1d821", "route_name": "ABJ TOWN EXPRESS - NYA/AREA1", "departure": "Nyanya", "arrival": "Area One", "distance_km": 15, "base_rate": 1500},
# #     {"_id": "67ea86762405e78f49b1d81c", "route_name": "ABJ TOWN EXPRESS - LUB/AREA1", "departure": "Lugbe", "arrival": "Area One", "distance_km": 20, "base_rate": 1500},
# #     {"_id": "67ea86762405e78f49b1d81d", "route_name": "ABJ TOWN EXPRESS - LUB/NYA", "departure": "Lugbe", "arrival": "Nyanya", "distance_km": 30, "base_rate": 1500},
# #     {"_id": "67ea86762405e78f49b1d81f", "route_name": "ABJ TOWN EXPRESS - AREA1/NYA", "departure": "Area One", "arrival": "Nyanya", "distance_km": 15, "base_rate": 1500}
# # ]

# # trains = [
# #     {"_id": "67d4e81a61abe421d4140d5f", "train_name": "Express A", "train_number": "101", "capacity": 10},
# #     {"_id": "67d4e81a61abe421d4140d62", "train_name": "Metro B", "train_number": "104", "capacity": 10},
# #     {"_id": "67d4e81a61abe421d4140d60", "train_name": "Metro A", "train_number": "102", "capacity": 10},
# #     {"_id": "67d4e81a61abe421d4140d61", "train_name": "Express B", "train_number": "103", "capacity": 10}
# # ]

# # # Helper functions
# # def generate_seat_number():
# #     return f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])}{random.randint(1, 10)}"

# # def generate_departure_time():
# #     # Generate a random departure time between 6:00 AM and 9:00 PM
# #     hour = random.randint(6, 21)
# #     minute = random.randint(0, 59)
# #     return datetime(2025, 4, random.randint(1, 30), hour, minute)

# # def generate_booking_data():
# #     route = random.choice(routes)
# #     train = random.choice(trains)
# #     available_seats = random.randint(1, train["capacity"])  # Random number of available seats
# #     total_seats = train["capacity"]
    
# #     departure_time = generate_departure_time()
# #     seat_number = generate_seat_number()

# #     booking_data = {
# #         "route_id": route["_id"],
# #         "train_id": train["_id"],
# #         "departure": route["departure"],  # Accessing correct route data
# #         "arrival": route["arrival"],      # Accessing correct route data
# #         "seat_number": seat_number,
# #         "price": round(route["base_rate"] * (1 + (0.05 * route["distance_km"])), 2),
# #         "departure_time": departure_time.strftime("%Y-%m-%d %H:%M:%S"),
# #         "departure_date": departure_time.strftime("%Y-%m-%d"),
# #     }
    
# #     return booking_data

# # # Generate synthetic data and save to a JSON file
# # def generate_synthetic_data(num_records, output_file="updated_synthetic_bookings.json"):
# #     bookings = []
# #     for _ in range(num_records):
# #         booking = generate_booking_data()
# #         bookings.append(booking)
    
# #     with open(output_file, "w") as f:
# #         json.dump(bookings, f, indent=4)

# #     print(f"Generated {num_records} synthetic bookings and saved to {output_file}")

# # # Generate the data
# # generate_synthetic_data(5000)
















# # import random
# # import json
# # from datetime import datetime, timedelta
# # import pytz

# # # Redefine the Nigeria timezone
# # nigeria_tz = pytz.timezone("Africa/Lagos")

# # # Your route, train, and booking data
# # routes = [
# #     {"_id": "67ea86762405e78f49b1d81e", "departure": "Area One", "arrival": "Lugbe", "base_rate": 1500, "distance_km": 20},
# #     {"_id": "67ea86762405e78f49b1d820", "departure": "Nyanya", "arrival": "Lugbe", "base_rate": 1500, "distance_km": 30},
# #     {"_id": "67ea86762405e78f49b1d821", "departure": "Nyanya", "arrival": "Area One", "base_rate": 1500, "distance_km": 15},
# #     {"_id": "67ea86762405e78f49b1d81c", "departure": "Lugbe", "arrival": "Area One", "base_rate": 1500, "distance_km": 20},
# #     {"_id": "67ea86762405e78f49b1d81d", "departure": "Lugbe", "arrival": "Nyanya", "base_rate": 1500, "distance_km": 30},
# #     {"_id": "67ea86762405e78f49b1d81f", "departure": "Area One", "arrival": "Nyanya", "base_rate": 1500, "distance_km": 15},
# # ]

# # trains = [
# #     {"_id": "67d4e81a61abe421d4140d5f", "train_name": "Express A", "train_number": "101", "capacity": 10, "status": "Active"},
# #     {"_id": "67d4e81a61abe421d4140d62", "train_name": "Metro B", "train_number": "104", "capacity": 10, "status": "Active"},
# #     {"_id": "67d4e81a61abe421d4140d60", "train_name": "Metro A", "train_number": "102", "capacity": 10, "status": "Active"},
# #     {"_id": "67d4e81a61abe421d4140d61", "train_name": "Express B", "train_number": "103", "capacity": 10, "status": "Active"},
# # ]

# # # Function to calculate dynamic fare
# # def calculate_dynamic_fare(route, departure_time, available_seats, total_seats):
# #     base_fare = route["base_rate"]
    
# #     # Peak hour surcharge (20% increase)
# #     peak_hours = [(8, 30), (11, 30), (14, 30), (18, 30)]
# #     departure_hour = departure_time.hour
# #     departure_minute = departure_time.minute
# #     if any(departure_hour == h and departure_minute == m for h, m in peak_hours):
# #         base_fare *= 1.2
    
# #     # Demand-based pricing (30% increase if less than 30% seats available)
# #     seat_availability_ratio = available_seats / total_seats
# #     if seat_availability_ratio < 0.3:
# #         base_fare *= 1.3
    
# #     return round(base_fare, 2)

# # # Function to save the synthetic dataset to a file
# # def save_to_file(data, filename="synthetic_bookings.json"):
# #     with open(filename, "w") as file:
# #         json.dump(data, file, indent=4)
# #     print(f"Data saved to {filename}")

# # # Generate synthetic bookings
# # def generate_synthetic_bookings(num_bookings=5000):
# #     bookings = []
# #     for _ in range(num_bookings):
# #         route = random.choice(routes)
# #         train = random.choice(trains)
        
# #         # Random departure date within the next 60 days
# #         departure_date = datetime.now() + timedelta(days=random.randint(1, 60))
# #         departure_time = datetime.combine(departure_date, datetime.strptime(random.choice(["08:30", "11:30", "14:30", "18:30"]), "%H:%M").time())
# #         departure_time = nigeria_tz.localize(departure_time)

# #         total_seats = train["capacity"]
# #         available_seats = random.randint(0, total_seats)  # Random available seats
# #         seat_number = f"A{random.randint(1, total_seats)}"  # Random seat

# #         price = calculate_dynamic_fare(route, departure_time, available_seats, total_seats)
# #         booking_date = departure_date - timedelta(days=random.randint(1, 30))  # Random booking date before departure

# #         booking = {
# #             "_id": str(random.randint(100000, 999999)),  # Random unique ID
# #             "passenger_name": f"Passenger {random.randint(1000, 9999)}",
# #             "phone_number": f"070{random.randint(10000000, 99999999)}",
# #             "route_id": route["_id"],
# #             "route_name": f"{route['departure']} - {route['arrival']}",
# #             "train_id": train["_id"],
# #             "train_name": train["train_name"],
# #             "departure": route["departure"],
# #             "arrival": route["arrival"],
# #             "seat_number": seat_number,
# #             "price": price,
# #             "departure_time": departure_time.strftime("%Y-%m-%d %H:%M"),
# #             "departure_date": departure_date.strftime("%Y-%m-%d"),
# #             "booking_date": booking_date.strftime("%Y-%m-%d %H:%M:%S"),
# #             "payment_status": random.choice(["Paid", "Pending", "Failed"]),
# #             "status": random.choice(["Confirmed", "Canceled"]),
# #         }

# #         bookings.append(booking)
    
# #     return bookings

# # # Generate and save the synthetic data
# # synthetic_bookings = generate_synthetic_bookings()
# # save_to_file(synthetic_bookings, "new_synthetic_bookings.json")
