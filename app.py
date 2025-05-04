from http import client
from flask import Flask, request, jsonify, render_template, send_file, flash, url_for, redirect, session
import pandas as pd
import joblib
import numpy as np
from pymongo import MongoClient, DESCENDING
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import gridfs
import certifi
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
import io
from flask_socketio import SocketIO, emit
from collections import defaultdict
from datetime import datetime, time, timezone, timedelta
from flask_cors import CORS
import pytz
import csv
from collections import defaultdict
import os
import certifi
from pymongo import MongoClient

# Flask App Configuration
app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'thiskeyissupposedtobeprivateandonlyknowbytheadmin'
CORS(app)



client = MongoClient(
    os.environ["MONGO_URI"],
    tlsCAFile=certifi.where()
)
db = client["e_ticketing"]  # Use your actual DB name here


# mongodb+srv://udofiaubong10:<db_password>@dsamessenger.tqp9u.mongodb.net/
# client = MongoClient("mongodb+srv://udofiaubong10:qAWzNlJT6x2vSCdb@dsamessenger.tqp9u.mongodb.net", tlsCAFile=certifi.where())
# client = MongoClient("mongodb+srv://udofiaubong10:qAWzNlJT6x2vSCdb@dsamessenger.tqp9u.mongodb.net", tlsCAFile=certifi.where())
# chat_db = client.get_database("dsachatDB")

# Set up database and GridFS
db = client["e_ticketing"]

users_collection = db["users"]
admin_collection = db["admin"]
routes_collection = db["routes"]  # Collection storing routes
stations_collection = db["stations"]  # Collection storing stations
train_schedules_collection = db["train_schedules"]  # Collection storing train schedules
bookings_collection = db["bookings"]
fare_predictions_collection = db["fare_predictions"]
fs = gridfs.GridFS(db)  # GridFS instance

# ==============================================================================================================================
# migrate db
# mongodump --db e_ticketing --out dump/
# mongorestore --uri "mongodb+srv://udofiaubong10:qAWzNlJT6x2vSCdb@dsamessenger.tqp9u.mongodb.net/e_ticketing" dump/e_ticketing
# 
# Database connection string
# database = "e_ticketing"   
# mongodb+srv://udofiaubong10:qAWzNlJT6x2vSCdb@dsamessenger.tqp9u.mongodb.net/e_ticketing?retryWrites=true&w=majority

# ==============================================================================================================================

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")



@app.route("/login")
def login():
    return render_template("login.html")



@app.route("/register")
def register():


    return render_template("register.html")


@app.route("/user_dashboard")
def user_dashboard():


    return render_template("user_dashboard.html")



def convert_objectid(doc):
    """Recursively converts ObjectId fields in a document to strings."""
    if isinstance(doc, list):
        return [convert_objectid(d) for d in doc]
    elif isinstance(doc, dict):
        return {k: str(v) if isinstance(v, ObjectId) else convert_objectid(v) for k, v in doc.items()}
    return doc

@app.route("/destination")
def destination():
    # Fetch all routes (excluding _id to avoid serialization issues)
    routes = list(routes_collection.find({}, {"_id": 0, "route_name": 1, "stations": 1}))

    # Fetch seat availability and convert all ObjectIds to strings
    seat_availability = list(train_schedules_collection.find({}, {"train_id": 1, "train_name": 1, "route_id": 1, "available_seats": 1, "seats": 1}))
    seat_availability = convert_objectid(seat_availability)  # Convert ObjectId recursively

    # Extract unique station names
    stations = list({station["station_name"] for route in routes for station in route.get("stations", [])})

    return render_template("destination.html", routes=routes, stations=stations, seat_availability=seat_availability)



@app.route("/booking_confirmation")
def book_confirmation():
    # fetch booking details to the booking confirmation page

    bookings = list(bookings_collection.find({}, {"_id": 0, "passenger_name": 1, "phone_number": 1, "route_name": 1, "train_name": 1, "departure": 1, "arrival": 1, "seat_number": 1, "price": 1, "departure_time": 1, "booking_date": 1}))



    return render_template("booking_confirmation.html", bookings=bookings)



@app.route("/success")
def success():
    # fetch booking details to the booking confirmation page

    bookings = list(bookings_collection.find({}, {"_id": 1, "passenger_name": 1, "phone_number": 1, "route_name": 1, "train_name": 1, "departure": 1, "arrival": 1, "seat_number": 1, "price": 1, "departure_time": 1, "booking_date": 1}))



    return render_template("success.html", bookings=bookings)

# ----------------------------------------------------------------------------------------
@app.route("/profile_picture/<user_id>")
def get_profile_picture(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user and "profile_picture" in user:
            file_id = user["profile_picture"]
            file_data = fs.get(ObjectId(file_id))  # Ensure file_id is an ObjectId
            return send_file(io.BytesIO(file_data.read()), mimetype="image/jpeg")
        return "No Image", 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------------


@app.route("/submit_register", methods=["POST"])
def submit_register():
    try:
        # Fetch data from the form
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password_hash")
        con_password = request.form.get("con_password_hash")
        role = request.form.get("role")
        status = request.form.get("status")
        profile_picture = request.files.get("profile_picture")

        print(f"Received data: {firstname}, {lastname}, {email}, {phone}")

        # Validation check
        if password != con_password:
            return jsonify({"success": False, "error": "Passwords do not match!"}), 400

        if users_collection.find_one({"email": email}):
            return jsonify({"success": False, "error": "Email is already registered!"}), 400

        hashed_password = generate_password_hash(password)

        # File handling with GridFS
        file_id = None
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            file_id = fs.put(profile_picture, filename=filename)
            print(f"Profile picture uploaded, file ID: {file_id}")
        else:
            print("No profile picture uploaded")

        # Prepare user data
        user_data = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "phone": phone,
            "password": hashed_password,
            "role": role,
            "status": status,
            "profile_picture": file_id,
            "timezone": datetime.now(timezone.utc).isoformat()
        }

        # Insert user data into MongoDB
        users_collection.insert_one(user_data)
        print("User registered successfully")

        # Emit event (to notify frontend)
        socketio.emit('user_registered', {'username': firstname + " " + lastname, 'email': email}, room=None)
        print("Event emitted for new user registration")

        return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the actual error
        return jsonify({"success": False, "error": "An error occurred while registering the user."}), 500

# -----------------------------------------------------------------------

# User login route
@app.route("/submit_login", methods=["POST"])
def submit_login():
    email = request.json.get("email")  # Use request.json since you're sending JSON data
    password = request.json.get("password")

    user = users_collection.find_one({"email": email})

    if user and check_password_hash(user["password"], password):
        session["user"] = user["email"]  # Store email in session
        session["role"] = user["role"]  # Store user role

        # Return a JSON response with success status and redirect URL
        return jsonify({
            "success": True,
            "redirect": url_for("user_dashboard")
        })
    else:
        return jsonify({
            "success": False,
            "error": "Invalid email or password!"
        }), 400
   
# -------------------------------------------------------------------
@socketio.on('user_registered')
def handle_user_registration(data):
    # Emit event to frontend to update the chart
    socketio.emit('user_registered', {'username': data['username'], 'email': data['email']}, broadcast=True)

# Other event
@socketio.on('payment_ticket_update')
def handle_payment_ticket(data):
    socketio.emit('payment_ticket_update', {'ticket_info': data}, broadcast=True)


# ------------------------------------------------------------------
# User login route
@app.route("/admin_login", methods=["POST"])
def admin_login():
    email = request.json.get("email")  # Use request.json since you're sending JSON data
    password = request.json.get("password")

    admin = admin_collection.find_one({"email": email})

    if admin and check_password_hash(admin["password"], password):
        session["user"] = admin["email"]  # Store email in session
        session["role"] = admin["role"]  # Store user role

        # Return a JSON response with success status and redirect URL
        return jsonify({
            "success": True,
            "redirect": url_for("dashboard")
        })
    else:
        return jsonify({
            "success": False,
            "error": "Invalid email or password!"
        }), 400
   


# -------------------------------------------------------------------

@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect(url_for("login"))

    user = {"email": session.get("user")}
    return render_template("admin.html", user=user, content="admin.html")
 
@app.route('/dashboard')
def dashboard():
    return render_template("admin.html", content="partials/dashboard.html")

@app.route('/users')
def users():
    return render_template("admin.html", content="partials/users.html")

@app.route('/tickets')
def tickets():
    return render_template("admin.html", content="partials/tickets.html")

@app.route('/trains')
def trains():
    return render_template("admin.html", content="partials/trains.html")

@app.route('/train_routes')
def stations():
    return render_template("admin.html", content="partials/train_routes.html")

@app.route('/payments')
def payments():
    return render_template("admin.html", content="partials/payments.html")

@app.route('/analytics')
def analytics():
    return render_template("admin.html", content="partials/analytics.html")

@app.route('/settings')
def settings():
    return render_template("admin.html", content="partials/settings.html")

# -------------------------------------------------------------------------------------


@app.route("/dashboard_stats", methods=["GET"])
def get_dashboard_stats():
    try:
        total_users = users_collection.count_documents({})
        total_trains = trains_collection.count_documents({})

        return jsonify({
            "total_users": total_users,
            "total_trains": total_trains
        }), 200
    except Exception as e:
        print("Error fetching dashboard stats:", str(e))
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------------------------
# User logout route
@app.route("/logout")
def logout():
    session.pop("user", None)  # Remove user from session
    session.pop("role", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ------------------------------------- USERS COLLECTIONS STARTS HERE ----------------------------------------------

users_collection = db["users"]

# Helper function to convert MongoDB documents
def serialize_user(user):
    user["_id"] = str(user["_id"])  # Convert _id to string
    if "profile_picture" in user and isinstance(user["profile_picture"], ObjectId):
        user["profile_picture"] = str(user["profile_picture"])  # Convert profile_picture ID
    return user

@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        users = list(users_collection.find())  # Fetch all users
        users = [serialize_user(user) for user in users]  # Convert ObjectId
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------- REGISTRATION VISUALIZATION -----------------------------------

@app.route("/user_registration_trend", methods=["GET"])
def user_registration_trend():
    try:
        # Fetch user registration timestamps
        users = list(users_collection.find({}, {"_id": 0, "timestamp": 1}).sort("timestamp", DESCENDING))

        # Check if users exist
        if not users:
            return jsonify({"error": "No users found"}), 404

        # Convert timestamps to human-readable dates
        registration_data = []
        for user in users:                                                                          
            if "timestamp" in user:
                try:
                    timestamp = user["timestamp"]

                    # Ensure timestamp is converted properly
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp)  # Convert from ISO string
                    elif isinstance(timestamp, int):
                        timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)  # Convert from UNIX timestamp

                    registration_data.append(timestamp.strftime("%Y-%m-%d"))
                except Exception as e:
                    print(f"Skipping invalid timestamp: {user['timestamp']} - Error: {e}")

        return jsonify({"dates": registration_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------- USERS COLLECTIONS ENDS HERE ----------------------------------------------


# ------------------------------------- TRAIN COLLECTIONS STARTS HERE ----------------------------------------------

trains_collection = db["trains"]

# Valid Train Statuses
VALID_STATUSES = {"Active", "Maintenance", "Out of Service"}  # Set of valid statuses

def validate_train_data(train_data):
    if train_data.get("status") not in VALID_STATUSES:
        raise ValueError("Invalid train status. Must be 'Active', 'Maintenance', or 'Out of Service'.")




# Route to update train status
@app.route("/update_train_status", methods=["POST"])
def update_train_status():
    data = request.json
    train_id = data.get("train_number")
    new_status = data.get("status")

    if not ObjectId.is_valid(train_id):
        return jsonify({"error": "Invalid train ID"}), 400

    if new_status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status. Must be 'Active', 'Maintenance', or 'Out of Service'."}), 400

    result = trains_collection.update_one(
        {"_id": ObjectId(train_id)},
        {"$set": {"status": new_status}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Train not found"}), 404

    return jsonify({"message": "Train status updated successfully"}), 200



# Route to get all trains
@app.route("/get_trains", methods=["GET"])
def get_trains():
    trains = list(trains_collection.find({}, {"_id": 1, "train_name": 1, "train_number": 1, "capacity": 1, "status": 1}))
    for train in trains:
        train["_id"] = str(train["_id"])  # Convert ObjectId to string
    return jsonify(trains), 200



# Get available trains for booking

def get_available_trains(route_id):
    # Fetch all scheduled trains for the route with available seats
    scheduled_trains = db.train_schedule.find({
        "route_id": ObjectId(route_id),
        "status": "Scheduled",
        "available_seats": {"$gt": 0}
    })

    available_trains = []
    for train in scheduled_trains:
        train_info = db.trains_collection.find_one({
            "_id": train["train_id"],
            "status": "Active"
        })

        if train_info:
            available_trains.append({
                "train_id": str(train["_id"]),
                "train_name": train["train_name"],
                "departure_time": train["departure_time"],
                "arrival_time": train["arrival_time"],
                "available_seats": train["available_seats"],
                "current_fare": train["dynamic_fare"]["current_fare"]
            })
    
    return available_trains


@app.route("/get_available_trains", methods=["GET"])
def get_available_trains_route():
    route_id = request.args.get("route_id")
    available_trains = get_available_trains(route_id)
    return jsonify({"trains": available_trains})

# ------------------------------------- TRAIN COLLECTIONS ENDS HERE -----------------------------------------------------


# ==========================GET AVAILABLE SEAT ======================================
train_schedules_collection = db["train_schedules"] 

@app.route("/get_available_seats", methods=["GET"])
def get_available_seats():
    route_id = request.args.get("route_id")
    departure_date = request.args.get("departure_date")

    if not route_id or not departure_date:
        return jsonify({"error": "Missing route_id or departure_date"}), 400

    try:
        schedule = train_schedules_collection.find_one({
            "route_id": ObjectId(route_id),
            "departure_date": departure_date
        })
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    if not schedule:
        return jsonify({"available_seats": []})  # Return an empty list instead of error

    return jsonify({"available_seats": schedule.get("available_seats", [])})


# ===================================== BOOKING/TICKETING ==================================================

# (DISPLAYED IN ADMIN)
@app.route("/get_bookings", methods=["GET"])
def get_bookings():
    ticket_bookings = list(bookings_collection.find({}, {
        "_id": 1, "passenger_name": 1, "phone_number": 1, "route_name": 1, "train_name": 1, 
        "departure": 1, "arrival": 1, "seat_number": 1, "price": 1, "departure_time": 1, 
        "booking_date": 1, "payment_status": 1, "booking_status": 1  # Added missing fields
    }))
    
    # Convert ObjectId to string
    for booking in ticket_bookings:
        booking["_id"] = str(booking["_id"])
    return jsonify(ticket_bookings), 200


# ===============================================================================================================

# ==============================================================================================================
# Route to get departure time and train detail

@app.route("/get_departure_time", methods=["POST"])
def get_departure_time():
    try:
        data = request.json
        route_id = data.get("route_id")
        departure_date = data.get("departure_date")

        if not route_id or not departure_date:
            return jsonify({"error": "Missing route_id or departure_date"}), 400

        schedule = train_schedules_collection.find_one({
            "route_id": ObjectId(route_id),
            "departure_date": departure_date
        })
        if not schedule:
            return jsonify({"error": "No schedule found for selected date and route"}), 404

        train = trains_collection.find_one({"_id": schedule["train_id"]})
        if not train:
            return jsonify({"error": "Train not found"}), 404

        route = routes_collection.find_one({"_id": ObjectId(route_id)})
        if not route:
            return jsonify({"error": "Route not found"}), 404

        # Convert capacity safely
        capacity = train.get("capacity")
        total_seats = int(capacity.get("$numberInt", 10)) if isinstance(capacity, dict) else int(capacity or 10)

        # Calculate available seats
        available_count = sum(1 for s in schedule["available_seats"] if s["status"] == "available")

        # Parse departure hour
        try:
            dep_hour = int(schedule["departure_time"].split(":")[0])
        except Exception:
            dep_hour = 0  # fallback

        # Determine peak hour (e.g., 6–9 AM, 17–20 PM)
        is_peak = 1 if (7 <= dep_hour <= 9 or 17 <= dep_hour <= 19) else 0

        return jsonify({
            "success": True,
            "train_id": str(schedule["train_id"]),
            "train_name": train["train_name"],
            "route_id": route_id,
            "route_name": route["route_name"],
            "departure_time": f"{departure_date} {schedule['departure_time']}",
            "arrival_time": f"{departure_date} {schedule['arrival_time']}",
            "available_seats": schedule["available_seats"],
            "available_count": available_count,
            "total_seats": total_seats,
            "departure_hour": dep_hour,
            "is_peak_hour": is_peak,
            "status": schedule["status"]
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ==================================================================

# def calculate_dynamic_fare(route, departure_time, available_seats, total_seats):
#     """
#     Calculate the fare dynamically based on distance, peak hours, and demand.
#     """
#     # Input validation
#     if total_seats <= 0:
#         raise ValueError("Total seats must be positive")
#     if available_seats < 0 or available_seats > total_seats:
#         raise ValueError(f"Available seats ({available_seats}) must be between 0 and total seats ({total_seats})")

#     base_rate = route["base_rate"]
#     distance_km = route["distance_km"]
    
#     # Distance multiplier (5% per km)
#     distance_multiplier = 1 + (0.05 * distance_km)

#     # Peak hours calculation (unchanged)
#     nigeria_time = pytz.timezone("Africa/Lagos")
#     departure_time_local = departure_time.astimezone(nigeria_time)
#     departure_hour = departure_time_local.hour
#     peak_factor = 1.2 if (7 <= departure_hour <= 9 or 17 <= departure_hour <= 19) else 1.0

#     # CORRECTED Demand factor calculation
#     seat_availability_ratio = available_seats / total_seats
    
#     if seat_availability_ratio > 0.7:
#         demand_factor = 1.0  # Normal price (70-100% seats available)
#     elif seat_availability_ratio > 0.3:
#         demand_factor = 1.2  # Medium demand (30-70% available)
#     else:
#         demand_factor = 1.5  # High demand (<30% available)

#     # Final calculation
#     final_fare = base_rate * distance_multiplier * peak_factor * demand_factor

#     # # === LOGGING TO CSV FOR MODEL TRAINING ===
#     log_file = "log_booking_data/fare_log.csv"
#     header = [
#         "distance_km",
#         "base_rate",
#         "departure_hour",
#         "is_peak_hour",
#         "seat_availability_ratio",
#         "available_seats",
#         "total_seats",
#         "distance_multiplier",
#         "peak_factor",
#         "demand_factor",
#         "final_fare"
#     ]

#     # Extract values to log
#     log_row = [
#         distance_km,
#         base_rate,
#         departure_hour,
#         1 if peak_factor > 1.0 else 0,
#         round(seat_availability_ratio, 2),
#         available_seats,
#         total_seats,
#         round(distance_multiplier, 2),
#         peak_factor,
#         demand_factor,
#         round(final_fare, 2)
#     ]

#     file_exists = os.path.isfile(log_file)
#     with open(log_file, mode='a', newline='') as file:
#         writer = csv.writer(file)
#         if not file_exists:
#             writer.writerow(header)
#         writer.writerow(log_row)


#     # Debug output with clearer labels
#     print("\n=== FARE CALCULATION BREAKDOWN ===")
#     print(f"BASE RATE: ₦{base_rate}")
#     print(f"DISTANCE: {distance_km}km → Multiplier: {distance_multiplier:.2f}x")
#     print(f"TIME: {departure_hour}:00 → Peak Factor: {peak_factor}x")
#     print(f"DEMAND: {available_seats}/{total_seats} seats available ({seat_availability_ratio:.0%}) → Factor: {demand_factor}x")
#     print(f"FINAL FARE: ₦{round(final_fare, 2)}")
#     print("=================================")
    
#     return round(final_fare, 2)

# =====================================================================

# # Flask Route to Calculate Fare

# @app.route("/calculate_fare", methods=["POST"])
# def calculate_fare():
#     try:
#         data = request.json
        
#         # Validate required fields
#         required_fields = ["train_id", "route_id", "departure_time", "available_seats", "total_seats"]
#         if not all(field in data for field in required_fields):
#             return jsonify({"error": "Missing required data"}), 400

#         # Get available seats count
#         available_seats = len([s for s in data["available_seats"] if s["status"] == "available"])
#         total_seats = data["total_seats"]  # From get_departure_time

#         # Debug log
#         print(f"Seat check: {available_seats} available / {total_seats} total")

#         if available_seats > total_seats:
#             raise ValueError(f"Data error: {available_seats} available > {total_seats} total seats")

#         # Get route details
#         route = routes_collection.find_one({"_id": ObjectId(data["route_id"])})
#         if not route:
#             return jsonify({"error": "Route not found"}), 404

#         # Calculate fare
#         departure_datetime = datetime.strptime(data["departure_time"], "%Y-%m-%d %H:%M")
#         fare = calculate_dynamic_fare(
#             route,
#             departure_datetime,
#             available_seats,
#             total_seats
#         )

#         return jsonify({
#             "fare": fare,
#             "metadata": {
#                 "available_seats": available_seats,
#                 "total_seats": total_seats,
#                 "seat_ratio": available_seats / total_seats
#             }
#         })

#     except Exception as e:
#         return jsonify({"error": f"Calculation error: {str(e)}"}), 500

# =========================================================================================


@app.route("/book_ticket", methods=["POST"])
def book_ticket():
    try:
        data = request.json

        # Validate required fields
        required_fields = ["passenger_name", "phone_number", "train_id", "route_id", "seat_number", "departure_time"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Convert IDs
        try:
            train_id = ObjectId(data["train_id"])
            route_id = ObjectId(data["route_id"])
        except:
            return jsonify({"error": "Invalid train_id or route_id format"}), 400

        # Parse departure time
        try:
            departure_datetime = datetime.strptime(data["departure_time"], "%Y-%m-%d %H:%M")
            departure_date = departure_datetime.strftime("%Y-%m-%d")
            departure_time = departure_datetime.strftime("%H:%M")
        except ValueError as e:
            return jsonify({"error": f"Invalid departure_time format: {str(e)}"}), 400

        # Find exact schedule
        train_schedule = train_schedules_collection.find_one({
            "train_id": train_id,
            "route_id": route_id,
            "departure_date": departure_date,
            "departure_time": departure_time,
            "available_seats.seat_number": data["seat_number"]
        })

        if not train_schedule:
            return jsonify({"error": "No matching schedule found for the specified train, route, date and time"}), 404

        # Check seat availability
        seat_to_book = next(
            (seat for seat in train_schedule["available_seats"] 
             if seat["seat_number"] == data["seat_number"]),
            None
        )

        if not seat_to_book:
            return jsonify({"error": f"Seat {data['seat_number']} doesn't exist in this schedule"}), 400
        if seat_to_book["status"] != "available":
            return jsonify({"error": f"Seat {data['seat_number']} is already booked"}), 400

        # Get train capacity
        train = trains_collection.find_one({"_id": train_id}, {"capacity": 1, "train_name": 1})
        if not train:
            return jsonify({"error": "Train not found"}), 404

        # Calculate fare
        available_count = len([s for s in train_schedule["available_seats"] if s["status"] == "available"])
        capacity = train.get("capacity", 10)
        total_seats = int(capacity.get("$numberInt", 10)) if isinstance(capacity, dict) else int(capacity)
        
        route = routes_collection.find_one({"_id": route_id})
        if not route:
            return jsonify({"error": "Route not found"}), 404

        # calculated_fare = calculate_dynamic_fare(route, departure_datetime, available_count, total_seats)

        # Prepare features for model prediction
        distance_km = route.get("distance_km", 0)
        departure_hour = departure_datetime.hour
        is_peak_hour = 1 if 7 <= departure_hour <= 9 or 17 <= departure_hour <= 20 else 0
        seat_availability_ratio = available_count / total_seats if total_seats else 0

        # Create DataFrame for model
        sample_df = pd.DataFrame([{
            "distance_km": distance_km,
            "departure_hour": departure_hour,
            "is_peak_hour": is_peak_hour,
            "seat_availability_ratio": seat_availability_ratio,
            "distance_peak_interaction": distance_km * is_peak_hour,
            "distance_demand_interaction": distance_km * (1 - seat_availability_ratio)
        }])

        # Predict fare and round to integer
        predicted_fare = int(round(model.predict(sample_df[enhanced_features])[0]))
        calculated_fare = predicted_fare

        fare_predictions_collection.insert_one({
            "distance_km": route.get("distance_km"),
            "departure_hour": departure_datetime.hour,
            "is_peak_hour": int(7 <= departure_datetime.hour <= 9 or 17 <= departure_datetime.hour <= 19),
            "seat_availability_ratio": available_count / total_seats,
            "predicted_fare": calculated_fare,
            "route_id": str(route_id),
            "train_id": str(train_id),
            "departure_date": departure_date,
            "timestamp": datetime.utcnow()
        })

        # Update seat status
        update_result = train_schedules_collection.update_one(
            {
                "_id": train_schedule["_id"],
                "available_seats.seat_number": data["seat_number"]
            },
            {
                "$set": {"available_seats.$.status": "booked"}
            }
        )

        if update_result.modified_count == 0:
            return jsonify({"error": "Failed to book seat - it may have been just taken by another user"}), 400

        # Create booking record
        booking_data = {
            "passenger_name": data["passenger_name"],
            "phone_number": data["phone_number"],
            "route_id": str(route_id),
            "route_name": data.get("route_name", train_schedule.get("route_name", "")),
            "train_id": str(train_id),
            "train_name": train.get("train_name", ""),
            "departure": data.get("departure", ""),
            "arrival": data.get("arrival", ""),
            "seat_number": data["seat_number"],
            "price": calculated_fare,
            "departure_time": data["departure_time"],
            "departure_date": departure_date,
            "booking_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "payment_status": "Paid",
            "status": "confirmed"
        }

        booking_id = bookings_collection.insert_one(booking_data).inserted_id
        booking_data["_id"] = str(booking_id)

        return jsonify({
            "message": "Booking successful!",
            "booking_id": str(booking_id),
            "seat_number": data["seat_number"],
            "status": "booked",
            "booking_data": booking_data
        })

    except Exception as e:
        return jsonify({"error": f"Booking failed: {str(e)}"}), 500
    
# ------------------------------------- ROUTE COLLECTIONS START HERE ----------------------------------------------------

routes_collection = db["routes"]


# Route to get all routes
@app.route("/get_routes", methods=["GET"])
def get_routes():
    # Explicitly include all needed fields
    routes = list(routes_collection.find({}, {
        "_id": 1,
        "departure": 1,
        "arrival": 1,
        "route_name": 1,
        "distance_km": 1,
        "base_rate": 1
    }))
    
    # Convert ObjectId to string
    for route in routes:
        route['_id'] = str(route['_id'])

    return jsonify(routes)



@app.route('/get_routes_detail', methods=['GET'])
def get_routes_detail():
    routes = list(routes_collection.find({}, {"_id": 1, "route_name": 1, "departure": 1, "arrival": 1, "distance_km": 1}))
    
    # Convert ObjectId to string
    for route in routes:
        route["_id"] = str(route["_id"])
    
    return jsonify(routes)


# Add this debug route to check raw data
@app.route('/debug_routes')
def debug_routes():
    routes = list(routes_collection.find({}))
    return jsonify([{**r, "_id": str(r["_id"])} for r in routes])



# ======================== MODEL TRAINING INTEGRATION =====================================================

# ========================== FARE PREDICTION ==================================================
@app.route('/test_form')
def test_form():

    return render_template('test_form.html')

@app.route('/analytics_1')
def analytics_1():

    return render_template('analytics_1.html')


# Load the trained model
model = joblib.load('fare_prediction/enhanced_linear_model.pkl')

# Define the enhanced features
enhanced_features = ['distance_km', 'departure_hour', 'is_peak_hour', 'seat_availability_ratio', 
                     'distance_peak_interaction', 'distance_demand_interaction']

@app.route('/predict_fare', methods=['POST'])
def predict_fare():
    # Get the JSON input from the request
    data = request.json

    # Required fields
    required_fields = ['distance_km', 'departure_hour', 'is_peak_hour', 'seat_availability_ratio']

    # Check for missing fields
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Validate and convert input types
        sample_df = pd.DataFrame([{
            'distance_km': int(data['distance_km']),
            'departure_hour': int(data['departure_hour']),
            'is_peak_hour': int(data['is_peak_hour']),
            'seat_availability_ratio': float(data['seat_availability_ratio'])
        }])

        # Compute interaction features
        sample_df['distance_peak_interaction'] = (
            sample_df['distance_km'] * sample_df['is_peak_hour']
        )
        sample_df['distance_demand_interaction'] = (
            sample_df['distance_km'] * (1 - sample_df['seat_availability_ratio'])
        )

        # Predict using the model
        predicted_fare = model.predict(sample_df[enhanced_features])

        # Round and convert to integer
        fare_int = int(round(predicted_fare[0]))

        # Optional: Log prediction input/output
        print(f"Input: {data}, Predicted fare: ₦{fare_int:,}")

        # Return the predicted fare
        return jsonify({'predicted_fare': f"₦{fare_int}", 'fare': fare_int})

    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500


# ==================================================================================================

@app.route('/predict_testform', methods=['POST'])
def predict_testform():
    # Get the JSON input from the request
    data = request.get_json()
    
    # Check if all required fields are in the request
    required_fields = ['distance_km', 'departure_hour', 'is_peak_hour', 'seat_availability_ratio']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Convert input data to a DataFrame
    sample_df = pd.DataFrame([data])
    
    # Calculate interaction terms
    sample_df['distance_peak_interaction'] = sample_df['distance_km'] * sample_df['is_peak_hour']
    sample_df['distance_demand_interaction'] = sample_df['distance_km'] * (1 - sample_df['seat_availability_ratio'])
    
    # Make prediction using the model
    predicted_fare = model.predict(sample_df[enhanced_features])
    
    # Return the predicted fare
    return jsonify({'predicted_fare': f"₦{predicted_fare[0]:,.1f}"})


# ========================= MODEL TRAINING INTEGRATION ENDS HERE ==================================================
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# ========================= MODEL TRAINING ANALYTICS STARTS HERE ==================================================


# Route to get fare analytics
@app.route("/fare_analytics")
def fare_analytics():
    pipeline = [
        {"$group": {
            "_id": "$route_id",
            "average_fare": {"$avg": "$predicted_fare"},
            "count": {"$sum": 1}
        }}
    ]
    avg_fares = list(fare_predictions_collection.aggregate(pipeline))

    labels = []
    data = []
    for item in avg_fares:
        route = routes_collection.find_one({"_id": ObjectId(item["_id"])})
        route_name = route.get("route_name", "Unknown Route")
        labels.append(route_name)
        data.append(round(item["average_fare"]))

    return render_template("fare_analytics.html", labels=labels, data=data)



@app.route("/fare_trend_data")
def fare_trend_data():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "departure_date": "$departure_date",
                    "route_id": "$route_id"
                },
                "average_fare": {"$avg": "$predicted_fare"}
            }
        },
        {
            "$sort": {"_id.departure_date": 1}
        }
    ]
    trend_data = list(fare_predictions_collection.aggregate(pipeline))

    formatted = {}
    for item in trend_data:
        date = item["_id"]["departure_date"]
        route_id = item["_id"]["route_id"]
        route = routes_collection.find_one({"_id": ObjectId(route_id)})
        route_name = route.get("route_name", "Unknown")

        if route_name not in formatted:
            formatted[route_name] = []
        formatted[route_name].append({"x": date, "y": round(item["average_fare"])})

    return jsonify(formatted)



@app.route("/fare_peak_comparison")
def fare_peak_comparison():
    pipeline = [
        {
            "$group": {
                "_id": {"is_peak_hour": "$is_peak_hour"},
                "average_fare": {"$avg": "$predicted_fare"}
            }
        }
    ]
    results = list(fare_predictions_collection.aggregate(pipeline))
    
    peak = next((r for r in results if r["_id"] == 1), {"average_fare": 0})
    off_peak = next((r for r in results if r["_id"] == 0), {"average_fare": 0})

    return jsonify({
        "labels": ["Off-Peak", "Peak"],
        "data": [round(off_peak["average_fare"]), round(peak["average_fare"])]
    })


@app.route("/fare_vs_demand")
def fare_vs_demand():
    docs = fare_predictions_collection.find({}, {
        "predicted_fare": 1,
        "seat_availability_ratio": 1,
        "_id": 0
    })

    data = [{"x": round(d["seat_availability_ratio"], 2), "y": d["predicted_fare"]} for d in docs if "seat_availability_ratio" in d]
    return jsonify(data)




@app.route("/payment_status_chart")
def payment_status_chart():
    pipeline = [
        {"$group": {"_id": "$payment_status", "count": {"$sum": 1}}}
    ]
    results = list(bookings_collection.aggregate(pipeline))
    return jsonify({
        "labels": [r["_id"] for r in results],
        "data": [r["count"] for r in results]
    })


@app.route("/tickets_per_day")
def tickets_per_day():
    pipeline = [
        {"$group": {"_id": "$departure_date", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    results = list(bookings_collection.aggregate(pipeline))
    return jsonify({
        "labels": [r["_id"] for r in results],
        "data": [r["count"] for r in results]
    })





if (__name__ == "__main__"):
    # print("Available Routes:")
    # print(app.url_map)
    socketio.run(app, host="0.0.0.0", port=5009, debug=True)