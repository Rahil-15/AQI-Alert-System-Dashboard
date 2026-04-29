# Project Report: Real-Time Air Quality Prediction and Alert System

## 1. Introduction
Air pollution is a growing concern globally, posing severe health risks to urban populations. The **Real-Time Air Quality Prediction and Alert System** is designed to mitigate these risks by proactively warning users of impending hazardous air conditions. Instead of merely displaying current data, this system leverages Machine Learning to predict future Air Quality Index (AQI) values and triggers real-time health alerts based on those predictions.

## 2. What is the System Alerting?
The core objective of this project is its **Alert Mechanism**. The system continuously monitors environmental metrics and feeds them into a predictive model. The model calculates the expected AQI, and the system then categorizes this prediction into three distinct Alert Levels to notify the user of the health risk:

- **🟢 Good (AQI < 100):** Air quality is considered satisfactory, and air pollution poses little or no risk. Safe for outdoor activities.
- **🟡 Moderate (AQI 100–200):** Air quality is acceptable; however, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.
- **🔴 Hazardous (AQI > 200):** Health warning of emergency conditions. The entire population is more likely to be affected. The system actively alerts users to remain indoors.

By predicting these levels *before* they occur, the system provides an early warning mechanism rather than a simple reactive display.

## 3. System Architecture
This project is built as a complete end-to-end MLOps pipeline, consisting of data ingestion, model training, and API deployment.

### 3.1. Data Pipeline
The project utilizes historical and real-time data mimicking the **OpenWeather API**. The data includes essential features required for accurate AQI prediction:
- Temperature
- Humidity
- Wind Speed

A specialized data generation script was developed to simulate 120 hours of localized weather and pollution metrics, enabling the model to learn time-series patterns effectively.

### 3.2. Machine Learning Model (LSTM)
The predictive core of the system is a **Long Short-Term Memory (LSTM)** Neural Network, built using TensorFlow/Keras.
- **Why LSTM?** Air quality is highly dependent on sequential, time-based trends (e.g., pollution accumulating over hours). LSTMs are specifically designed to remember long-term dependencies in time-series data.
- **Training:** The model takes a sequence of past weather and AQI data (Sequence Length = 6) and learns the correlation between temperature, humidity, wind speed, and resulting air quality to predict the next AQI value.

### 3.3. Flask API Backend
The trained LSTM model is deployed as a production-ready REST API using **Flask**. The backend exposes critical endpoints:
- `/predict`: Accepts geographic coordinates (`lat`, `lon`) or a `city` name. It fetches live OpenWeather data for that specific location, processes it through the LSTM model, and returns the predicted AQI alongside the calculated **Alert Status**.
- `/aqi-status`: A lightweight endpoint to quickly fetch the current AQI without running the predictive model.
- **Reverse Geocoding:** The backend integrates the OpenWeather Reverse Geocoding API to dynamically translate raw GPS coordinates back into readable City Names.

### 3.4. Dynamic HTML Dashboard
The user-facing component is a modern, responsive web dashboard built with HTML, CSS (featuring a Glassmorphism design), and JavaScript.
- **Automatic Geolocation:** Upon opening, the dashboard uses the HTML5 Geolocation API to detect the user's exact physical location, automatically fetching their local Air Quality Prediction.
- **Location Search:** Users can manually type in any city worldwide (e.g., "London", "Tokyo") to view its predicted AQI.
- **Dynamic Alert UI:** The dashboard's central Alert Box dynamically changes color (Green, Yellow, or Red) based on the Alert Level provided by the API, offering an immediate visual warning to the user.

## 4. Conclusion
This project successfully demonstrates a full-stack, AI-powered predictive system. By combining time-series Machine Learning with real-time API integrations and a dynamic front-end dashboard, the system effectively acts as an early-warning mechanism to help individuals make informed decisions about their exposure to air pollution.
