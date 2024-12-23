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

# Flask app setup
api = Flask(__name__)
CORS(api)

@api.route('/')
def home_page():
    return jsonify({"message": "API Server Running"}), 200

@api.route('/alert', methods=['GET'])
def create_alert():
    """Store alert data in MongoDB."""
    type1 = request.args.get('type')
    message1 = request.args.get('message')

    if not type1 or not message1:
        return jsonify({"error": "Missing 'type' or 'message' query parameter."}), 400

    data = {
        "type": type1,
        "message": message1,
        "timestamp": datetime.utcnow()
    }
    result = alertsCollection.insert_one(data)
    data["_id"] = str(result.inserted_id)

    return jsonify({"message": "Alert stored successfully", "data": data}), 201

@api.route('/store', methods=['GET'])
def store_data():
    """Store generic data in MongoDB."""
    label = request.args.get('label')
    value = request.args.get('value')

    if not label or not value:
        return jsonify({"error": "Missing 'label' or 'value' query parameter."}), 400

    try:
        value = float(value)
    except ValueError:
        return jsonify({"error": "'value' must be numeric."}), 400

    data = {
        "label": label,
        "value": value,
        "timestamp": datetime.utcnow()
    }
    result = collection.insert_one(data)
    data["_id"] = str(result.inserted_id)

    return jsonify({"message": "Data stored successfully", "data": data}), 201

@api.route('/store-sensor-data', methods=['POST'])
def store_sensor_data():
    """Store sensor data (MAX30102, DHT11) in MongoDB."""
    try:
        data = request.json

        sensor_type = data.get('sensor_type')
        sensor_data = data.get('sensor_data')

        if not sensor_type or not sensor_data:
            return jsonify({"error": "Missing 'sensor_type' or 'sensor_data'"}), 400

        if sensor_type == "max30102":
            heart_rate = sensor_data.get("heart_rate")
            spo2 = sensor_data.get("spo2")
            if heart_rate is None or spo2 is None:
                return jsonify({"error": "Missing 'heart_rate' or 'spo2' for MAX30102"}), 400

            document = {
                "sensor_type": sensor_type,
                "heart_rate": heart_rate,
                "spo2": spo2,
                "timestamp": datetime.utcnow()
            }
            result = collection.insert_one(document)

        elif sensor_type == "dht11":
            temperature = sensor_data.get("temperature")
            humidity = sensor_data.get("humidity")
            if temperature is None or humidity is None:
                return jsonify({"error": "Missing 'temperature' or 'humidity' for DHT11"}), 400

            document = {
                "sensor_type": sensor_type,
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": datetime.utcnow()
            }
            result = collection.insert_one(document)

        else:
            return jsonify({"error": f"Unsupported sensor type '{sensor_type}'"}), 400

        document["_id"] = str(result.inserted_id)
        return jsonify({"message": "Sensor data stored successfully", "data": document}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/get-data', methods=['GET'])
def get_data():
    """Retrieve all stored data."""
    try:
        data = list(collection.find({}, {"_id": 0}))
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/get-alerts', methods=['GET'])
def get_alerts():
    """Retrieve all alerts."""
    try:
        data = list(alertsCollection.find({}, {"_id": 0}))
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/toggle-device', methods=['POST'])
def toggle_device():
    """Toggle the state of a device."""
    try:
        data = request.json
        device_id = data.get("device_id")

        if not device_id:
            return jsonify({"error": "Missing 'device_id' parameter."}), 400

        device = devicesCollection.find_one({"device_id": device_id})
        if not device:
            return jsonify({"error": f"Device with ID {device_id} not found."}), 404

        new_state = "on" if device.get("state", "off") == "off" else "off"
        devicesCollection.update_one({"device_id": device_id}, {"$set": {"state": new_state}})

        return jsonify({"message": f"Device {device_id} toggled", "state": new_state}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/get-devices', methods=['GET'])
def get_devices():
    """Retrieve all devices and their states."""
    try:
        devices = list(devicesCollection.find({}, {"_id": 0}))
        return jsonify(devices), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    api.run(host='0.0.0.0', port=2000, debug=True)