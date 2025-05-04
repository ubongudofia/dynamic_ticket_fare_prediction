from datetime import datetime
import pytz

def fare_breakdown(record):
    base_rate = 1500
    distance_km = record["distance_km"]
    departure_time_str = record["departure_time"]
    
    departure_time = datetime.strptime(departure_time_str, "%Y-%m-%d %H:%M:%S")
    nigeria_tz = pytz.timezone("Africa/Lagos")
    departure_time_local = nigeria_tz.localize(departure_time)
    departure_hour = departure_time_local.hour

    distance_multiplier = 1 + (0.05 * distance_km)
    peak_factor = 1.2 if (7 <= departure_hour <= 9 or 17 <= departure_hour <= 19) else 1.0
    actual_price = record["price"]
    price_without_demand = base_rate * distance_multiplier * peak_factor
    estimated_demand_factor = round(actual_price / price_without_demand, 2)

    print("\n=== FARE BREAKDOWN ===")
    print(f"Route: {record['route_name']}")
    print(f"Train: {record['train_name']}")
    print(f"Departure: {record['departure_time']} ({'Peak' if peak_factor > 1.0 else 'Off-peak'})")
    print(f"Distance: {distance_km} km → Multiplier: {distance_multiplier:.2f}")
    print(f"Base Rate: ₦{base_rate}")
    print(f"Peak Factor: {peak_factor}x")
    print(f"Estimated Demand Factor: {estimated_demand_factor}x")
    print(f"→ Calculated Fare: ₦{base_rate} × {distance_multiplier:.2f} × {peak_factor} × {estimated_demand_factor} = ₦{actual_price}")
    print("=======================\n")



# Call the function with your dataset
# sample_record = {
#     "route_name": "ABJ TOWN EXPRESS - AREA1/LUB",
#         "train_name": "Metro B",
#         "departure": "Area One",
#         "arrival": "Lugbe",
#         "seat_number": "A1",
#         "price": 4320,
#         "departure_time": "2025-06-30 08:30:00",
#         "departure_date": "2025-06-30",
#         "distance_km": 20
# }


# sample_record = {
#     "route_name": "ABJ TOWN EXPRESS - LUB/NYA",
#     "train_name": "Express A",
#     "departure": "Lugbe",
#     "arrival": "Nyanya",
#     "seat_number": "A5",
#     "price": 4129.6,
#     "departure_time": "2025-04-16 12:30:00",
#     "departure_date": "2025-04-16",
#     "distance_km": 30
# }


sample_record = {
    "route_name": "ABJ TOWN EXPRESS - AREA1/LUB",
    "train_name": "Metro B",
    "departure": "Area One",
    "arrival": "Lugbe",
    "seat_number": "A1",
    "price": 4320,
    "departure_time": "2025-06-30 08:30:00",
    "departure_date": "2025-06-30",
    "distance_km": 20
}





# Example input from model train_dataset_new.py
# sample_record = {
#     "route_name": "ABJ TOWN EXPRESS - LUB/NYA",
#     "train_name": "Express A",
#     "departure": "Lugbe",
#     "arrival": "Nyanya",
#     "seat_number": "A5",
#     "price": 4546,
#     "departure_time": "2025-04-16 12:30:00",
#     "departure_date": "2025-04-16",
#     "distance_km": 30
# }

fare_breakdown(sample_record)
