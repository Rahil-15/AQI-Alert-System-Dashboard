from flask import Flask, jsonify, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import MeanAbsoluteError
import requests
import numpy as np
import logging
from datetime import datetime
from prometheus_client import Counter, generate_latest
from flask import Response

# Initialize the Flask app
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the trained LSTM model
MODEL_PATH = "lstm_model.h5"
custom_objects = {
    "mse": MeanSquaredError(),
    "mae": MeanAbsoluteError()
}
model = load_model(MODEL_PATH, custom_objects=custom_objects)
logger.info(f"Loaded model from {MODEL_PATH}")

# Define the feature order expected by the model
FEATURE_ORDER = ['aqi', 'temperature', 'humidity', 'wind_speed']
SEQUENCE_LENGTH = 6  # Match the sequence length used in training

# OpenWeather API configuration
API_KEY = "119e24626ffc881be87270bae2f7ba40"  # Replace with your valid OpenWeather API key
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
REVERSE_GEO_URL = "http://api.openweathermap.org/geo/1.0/reverse"

CITY_CONFIG = {
    "lat": 33.6844,
    "lon": 73.0479,
    "name": "Islamabad"
}

# Create a counter for predictions
prediction_requests = Counter('prediction_requests_total', 'Total Prediction Requests')
prediction_success = Counter('prediction_success_total', 'Successful Predictions')
prediction_failure = Counter('prediction_failure_total', 'Failed Predictions')

def get_coordinates(city_name):
    """Fetch coordinates for a given city name."""
    try:
        params = {
            "q": city_name,
            "limit": 1,
            "appid": API_KEY
        }
        response = requests.get(GEO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            return data[0]["lat"], data[0]["lon"], data[0]["name"]
        return None, None, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching coordinates for {city_name}: {e}")
        return None, None, None

def get_city_from_coordinates(lat, lon):
    """Fetch city name for given coordinates."""
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "limit": 1,
            "appid": API_KEY
        }
        response = requests.get(REVERSE_GEO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            return data[0].get("name", "Unknown Location")
        return "Unknown Location"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching city for coordinates {lat}, {lon}: {e}")
        return "Unknown Location"

def fetch_live_data(lat=CITY_CONFIG["lat"], lon=CITY_CONFIG["lon"]):
    """Fetch live weather and pollution data for given coordinates."""
    try:
        # Fetch weather data
        weather_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric"
        }
        weather_response = requests.get(WEATHER_URL, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Fetch pollution data
        pollution_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY
        }
        pollution_response = requests.get(POLLUTION_URL, params=pollution_params)
        pollution_response.raise_for_status()
        pollution_data = pollution_response.json()

        return weather_data, pollution_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching live data: {e}")
        return None, None

def process_live_data(weather_data, pollution_data):
    """Process live data into the required format."""
    try:
        # Extract weather features
        processed_data = {
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "pressure": weather_data["main"]["pressure"],
            "wind_speed": weather_data["wind"]["speed"],
            "aqi": 0  # Placeholder for AQI
        }

        # Extract AQI from pollution data
        if pollution_data and "list" in pollution_data and pollution_data["list"]:
            processed_data["aqi"] = pollution_data["list"][0]["main"]["aqi"]

        return processed_data

    except KeyError as e:
        logger.error(f"KeyError in processing data: {e}")
        return None

def get_aqi_alert(aqi):
    """Determine the alert status based on AQI value."""
    if aqi < 100:
        return "Good"
    elif aqi <= 200:
        return "Moderate"
    else:
        return "Hazardous"

@app.route("/", methods=["GET"])
def home():
    """Serve the HTML Dashboard."""
    return render_template("index.html")

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), content_type='text/plain')

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route("/aqi-status", methods=["GET"])
def aqi_status():
    """Fetch live data and return current AQI status without ML prediction."""
    try:
        city_name = request.args.get("city")
        req_lat = request.args.get("lat")
        req_lon = request.args.get("lon")
        
        lat, lon, resolved_city = CITY_CONFIG["lat"], CITY_CONFIG["lon"], CITY_CONFIG["name"]
        
        if city_name:
            lat, lon, resolved_city = get_coordinates(city_name)
            if lat is None:
                return jsonify({"error": f"City '{city_name}' not found"}), 404
        elif req_lat and req_lon:
            lat, lon = req_lat, req_lon
            resolved_city = get_city_from_coordinates(lat, lon)

        weather_data, pollution_data = fetch_live_data(lat, lon)
        if not weather_data or not pollution_data:
            return jsonify({"error": "Failed to fetch live data"}), 500
        
        live_data = process_live_data(weather_data, pollution_data)
        if not live_data:
            return jsonify({"error": "Failed to process live data"}), 500
            
        current_aqi = live_data.get("aqi", 0)
        return jsonify({
            "city": resolved_city,
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "current_aqi": current_aqi,
            "status": get_aqi_alert(current_aqi),
            "live_data": live_data
        }), 200
    except Exception as e:
        logger.error(f"Error in aqi-status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/predict", methods=["GET", "POST"])
def predict():
    """
    Fetch live data, process it, and return AQI prediction with Alert Status.
    Accepts 'city' as a query parameter.
    """
    prediction_requests.inc()  # Increment the prediction requests counter
    try:
        city_name = request.args.get("city")
        req_lat = request.args.get("lat")
        req_lon = request.args.get("lon")
        
        lat, lon, resolved_city = CITY_CONFIG["lat"], CITY_CONFIG["lon"], CITY_CONFIG["name"]
        
        if city_name:
            lat, lon, resolved_city = get_coordinates(city_name)
            if lat is None:
                prediction_failure.inc()
                return jsonify({"error": f"City '{city_name}' not found"}), 404
        elif req_lat and req_lon:
            lat, lon = req_lat, req_lon
            resolved_city = get_city_from_coordinates(lat, lon)

        # Fetch live data
        weather_data, pollution_data = fetch_live_data(lat, lon)
        if not weather_data or not pollution_data:
            prediction_failure.inc()  # Increment the failure counter
            return jsonify({"error": "Failed to fetch live data"}), 500

        # Process the data
        live_data = process_live_data(weather_data, pollution_data)
        if not live_data:
            prediction_failure.inc()  # Increment the failure counter
            return jsonify({"error": "Failed to process live data"}), 500

        # Prepare input sequence for the LSTM model
        input_sequence = [[live_data[feature] for feature in FEATURE_ORDER]] * SEQUENCE_LENGTH
        input_sequence = np.array(input_sequence).reshape(1, SEQUENCE_LENGTH, len(FEATURE_ORDER))

        # Predict AQI
        prediction = model.predict(input_sequence).flatten()[0]
        prediction = float(prediction)
        
        # Get Alert Status
        alert_status = get_aqi_alert(prediction)

        # Increment the success counter
        prediction_success.inc()

        # Return the prediction
        return jsonify({
            "city": resolved_city,
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "predicted_aqi": prediction,
            "status": alert_status,
            "live_data": live_data
        }), 200

    except Exception as e:
        prediction_failure.inc()  # Increment the failure counter
        logger.error(f"Error during prediction: {e}")
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
