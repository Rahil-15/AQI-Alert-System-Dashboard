import json
import os
import random
from datetime import datetime, timedelta

def generate_mock_data():
    weather_dir = 'data/weather'
    pollution_dir = 'data/pollution'
    
    os.makedirs(weather_dir, exist_ok=True)
    os.makedirs(pollution_dir, exist_ok=True)
    
    start_time = datetime.utcnow() - timedelta(days=5)
    
    for day in range(5):
        weather_records = []
        pollution_records = []
        
        for hour in range(24):
            current_time = start_time + timedelta(days=day, hours=hour)
            timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Weather record
            weather_records.append({
                'city': 'Islamabad',
                'timestamp': timestamp_str,
                'temperature': round(random.uniform(15.0, 35.0), 2),
                'humidity': random.randint(30, 90),
                'pressure': random.randint(1000, 1020),
                'wind_speed': round(random.uniform(0.0, 10.0), 2),
                'weather_condition': random.choice(['Clear', 'Clouds', 'Rain'])
            })
            
            # Pollution record
            pollution_records.append({
                'city': 'Islamabad',
                'timestamp': timestamp_str,
                'aqi': random.randint(1, 5),
                'co': round(random.uniform(200.0, 800.0), 2),
                'no2': round(random.uniform(5.0, 50.0), 2),
                'o3': round(random.uniform(10.0, 100.0), 2),
                'pm2_5': round(random.uniform(5.0, 150.0), 2),
                'pm10': round(random.uniform(10.0, 200.0), 2)
            })
            
        file_timestamp = (start_time + timedelta(days=day)).strftime('%Y%m%d')
        
        with open(os.path.join(weather_dir, f'weather_data_{file_timestamp}.json'), 'w') as f:
            json.dump(weather_records, f, indent=4)
            
        with open(os.path.join(pollution_dir, f'pollution_data_{file_timestamp}.json'), 'w') as f:
            json.dump(pollution_records, f, indent=4)
            
    print("Mock data generated successfully in data/weather and data/pollution.")

if __name__ == "__main__":
    generate_mock_data()
