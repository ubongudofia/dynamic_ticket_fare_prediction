import csv
import random
from datetime import datetime, timedelta
import pytz

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

def generate_synthetic_fare_records(num_records=5000, output_file="synthetic_fare_data.csv"):
    nigeria_tz = pytz.timezone("Africa/Lagos")

    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "distance_km", "base_rate", "departure_hour", "is_peak_hour",
            "seat_availability_ratio", "available_seats", "total_seats",
            "distance_multiplier", "peak_factor", "demand_factor", "final_fare"
        ])

        for _ in range(num_records):
            route = random.choice(routes)
            train = random.choice(trains)

            distance_km = route["distance_km"]
            base_rate = route["base_rate"]
            total_seats = train["capacity"]
            available_seats = random.randint(0, total_seats)
            seat_availability_ratio = round(available_seats / total_seats, 2)

            # Random time for departure
            departure_hour = random.randint(0, 23)
            departure_time = datetime(2024, 1, 1, departure_hour, 0, tzinfo=pytz.utc).astimezone(nigeria_tz)

            # Peak hour
            is_peak_hour = 1 if 7 <= departure_hour <= 9 or 17 <= departure_hour <= 19 else 0
            peak_factor = 1.2 if is_peak_hour else 1.0

            # Demand factor
            if seat_availability_ratio > 0.7:
                demand_factor = 1.0
            elif seat_availability_ratio > 0.3:
                demand_factor = 1.2
            else:
                demand_factor = 1.5

            # Correct distance multiplier
            distance_multiplier = round(1 + (0.05 * distance_km), 2)

            # Final fare
            final_fare = round(base_rate * distance_multiplier * peak_factor * demand_factor, 2)

            writer.writerow([
                distance_km, base_rate, departure_hour, is_peak_hour,
                seat_availability_ratio, available_seats, total_seats,
                distance_multiplier, peak_factor, demand_factor, final_fare
            ])

    print(f"✅ Generated {num_records} synthetic fare records in '{output_file}'")

# Call the function
generate_synthetic_fare_records()
