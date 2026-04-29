# Real-Time Air Quality Prediction & Alert System

An end-to-end **Machine Learning + Web Application** that predicts future Air Quality Index (AQI) and provides **real-time health alerts** based on predicted pollution levels.

> Unlike traditional AQI dashboards, this system is **proactive** — it predicts air quality *before it becomes hazardous*.

---

##  Features

- **AQI Prediction using LSTM (Deep Learning)**
- **Real-time Data Integration (OpenWeather API simulation)**
- **Smart Alert System (Good / Moderate / Hazardous)**
- **Location-based Prediction (Auto + Manual Search)**
- **Reverse Geocoding (Coordinates → City Name)**
- **Interactive Web Dashboard (Glassmorphism UI)**
- **Flask REST API Backend**

---

## Tech Stack

### Machine Learning
- Python
- TensorFlow / Keras (LSTM)

### Backend
- Flask (REST API)
- OpenWeather API (for live data)

### Frontend
- HTML
- CSS (Glassmorphism UI)
- JavaScript

---

## How It Works

### 1. Data Pipeline
- Uses environmental features:
  - Temperature
  - Humidity
  - Wind Speed
- Simulated dataset (120 hours) to mimic real-world AQI trends

---

### 2. Model (LSTM)
- Sequence Length: 6
- Learns time-series dependencies
- Predicts **next AQI value**

---

### 3. Alert System

| AQI Range | Status       | Description |
|----------|-------------|------------|
| < 100    | 🟢 Good      | Safe for outdoor activities |
| 100–200  | 🟡 Moderate  | Sensitive groups at risk |
| > 200    | 🔴 Hazardous | Health warning, stay indoors |

---

### 4. Backend API

| Endpoint       | Description |
|---------------|------------|
| `/predict`     | Predict AQI using city or coordinates |
| `/aqi-status`  | Get current AQI status |

---

### 5. Frontend Dashboard
- Auto-detects user location
- Search any city worldwide
- Dynamic UI based on AQI level
- Real-time updates



---

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/aqi-alert-system.git
cd aqi-alert-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Flask Server
```bash
python app.py
```

### 4. Open Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
```

---

## Use Cases
- Smart City Monitoring Systems
- Health Advisory Applications
- Wearable Pollution Alert Devices
- Environmental Awareness Platforms

---

## Limitations
- Uses simulated dataset (not full real-world sensor data)
- Limited features (no PM2.5, PM10, CO, NO₂)
- Prediction depends on API data accuracy

---

##  Future Improvements
 - Integrate real-time IoT pollution sensors
 - Add advanced pollutants (PM2.5, NO₂, CO)
 - Deploy on AWS / Docker
 - Mobile app with push notifications
 - Upgrade model (Transformer / Hybrid models)~

---

## Contributing

Contributions are welcome!
Feel free to fork this repo and submit a pull request.

---

## License

This project is open-source and available under the MIT License.

---

##  Key Highlight

This project transforms AQI monitoring from a reactive system into a predictive early-warning system, helping users take preventive action against air pollution.