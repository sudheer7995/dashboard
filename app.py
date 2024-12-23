from pymongo import MongoClient
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# MongoDB setup
client = MongoClient("mongodb+srv://parvathanenimadhu:madhu123@cluster0.yaaw6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['makeskilled']
collection = db['iotdata-test']
alertsCollection = db['alerts']
devicesCollection = db['devices']

api = Flask(__name__)
CORS(api)

@api.route('/')
def homePage():
    return jsonify({"message": "API Server Running"}), 200

@api.route('/store-sensor-data', methods=['POST'])
def store_sensor_data():
    """Store sensor data (MAX30102, DHT11) in MongoDB."""
    try:
        # Parse JSON body
        data = request.json

        sensor_type = data.get('sensor_type')  # max30102 or dht11
        sensor_data = data.get('sensor_data')  # Actual sensor readings

        if not sensor_type or not sensor_data:
            return jsonify({"error": "Missing 'sensor_type' or 'sensor_data'"}), 400

        # Validate and process data based on sensor type
        if sensor_type == "max30102":
            # Expecting heart rate and SpO2
            heart_rate = sensor_data.get("heart_rate")
            spo2 = sensor_data.get("spo2")
            if heart_rate is None or spo2 is None:
                return jsonify({"error": "Missing 'heart_rate' or 'spo2' for MAX30102"}), 400
            
            # Store data in MongoDB
            document = {
                "sensor_type": sensor_type,
                "heart_rate": heart_rate,
                "spo2": spo2,
                "timestamp": datetime.utcnow()
            }
            result = collection.insert_one(document)

        elif sensor_type == "dht11":
            # Expecting temperature and humidity
            temperature = sensor_data.get("temperature")
            humidity = sensor_data.get("humidity")
            if temperature is None or humidity is None:
                return jsonify({"error": "Missing 'temperature' or 'humidity' for DHT11"}), 400

            # Store data in MongoDB
            document = {
                "sensor_type": sensor_type,
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": datetime.utcnow()
            }
            result = collection.insert_one(document)

        else:
            return jsonify({"error": f"Unsupported sensor type '{sensor_type}'"}), 400

        document["_id"] = str(result.inserted_id)  # Convert ObjectId to string for JSON serialization
        return jsonify({"message": "Sensor data stored successfully", "data": document}), 201

    except Exception as e:
        return jsonify({"error": str(e)}),
