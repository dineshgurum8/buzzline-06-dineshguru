import json
import os
from collections import deque
from kafka import KafkaConsumer
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dotenv import load_dotenv
from utils.alert_utils import send_sms_alert
import time

# Load environment variables
load_dotenv()

print("Twilio Account SID:", os.getenv("TWILIO_ACCOUNT_SID"))
print("Twilio Auth Token:", os.getenv("TWILIO_AUTH_TOKEN"))
print("Twilio Phone Number:", os.getenv("TWILIO_PHONE_NUMBER"))

# Kafka Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sensor_data")

# Anomaly Detection Thresholds
VIBRATION_THRESHOLD = float(os.getenv("VIBRATION_THRESHOLD", 8.0))  # mm/s
TEMPERATURE_THRESHOLD = float(os.getenv("TEMPERATURE_THRESHOLD", 80.0))  # °C
SOUND_LEVEL_THRESHOLD = float(os.getenv("SOUND_LEVEL_THRESHOLD", 85.0))  # dB

# Data Storage for Live Plot
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 50))
timestamps = deque(maxlen=WINDOW_SIZE)
vibrations = deque(maxlen=WINDOW_SIZE)
temperatures = deque(maxlen=WINDOW_SIZE)
sound_levels = deque(maxlen=WINDOW_SIZE)

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

def check_anomalies(sensor_data):
    """Check for anomalies and send alerts if thresholds are exceeded."""
    alert_message = []
    if sensor_data["vibration"] > VIBRATION_THRESHOLD:
        alert_message.append(f"⚠ High Vibration Alert: {sensor_data['vibration']} mm/s")
    if sensor_data["temperature"] > TEMPERATURE_THRESHOLD:
        alert_message.append(f"🔥 High Temperature Alert: {sensor_data['temperature']} °C")
    if sensor_data["sound_level"] > SOUND_LEVEL_THRESHOLD:
        alert_message.append(f"🔊 High Sound Level Alert: {sensor_data['sound_level']} dB")
    
    if alert_message:
        alert_text = "\n".join(alert_message)
        print(alert_text)
        send_sms_alert(alert_text)

def process_message(message):
    """Process and store received sensor data."""
    sensor_data = message.value
    print(f"Received data: {sensor_data}")  # Debug print to check data
    timestamps.append(sensor_data["timestamp"])
    vibrations.append(sensor_data["vibration"])
    temperatures.append(sensor_data["temperature"])
    sound_levels.append(sensor_data["sound_level"])

    # Debug print for temperature data
    print(f"Current temperatures: {temperatures}")
    
    check_anomalies(sensor_data)

def create_nested_pie_chart():
    """Create a nested pie chart for temperature changes."""
    # Wait for temperature data to be available
    while not temperatures:
        print("Waiting for temperature data...")
        time.sleep(1)  # Wait for 1 second before checking again

    temp = temperatures[-1]

    # Handle cases where the temperature is NaN or invalid
    if temp is None or temp != temp:  # Check if temp is NaN
        print("Invalid temperature data.")
        return

    # Define categories based on temperature range
    low_temp = temp if temp <= 20 else 0
    medium_temp = temp if 20 < temp <= 50 else 0
    high_temp = temp if temp > 50 else 0

    # If all categories are 0, avoid plotting
    if not any([low_temp, medium_temp, high_temp]):
        print("Temperature data does not fall into any defined range.")
        return

    # Create the nested pie chart (2 layers)
    fig, ax = plt.subplots(figsize=(7, 7))

    # Pie chart for low, medium, and high temperature
    outer_labels = ['Low', 'Medium', 'High']
    outer_sizes = [low_temp, medium_temp, high_temp]
    outer_colors = ['#ff9999', '#66b3ff', '#99ff99']

    # Inner pie chart for temperature values
    inner_labels = [f"Temp: {temp}°C"]
    inner_sizes = [temp]
    inner_colors = ['#ffcc99']

    ax.pie(outer_sizes, labels=outer_labels, colors=outer_colors, autopct='%1.1f%%', startangle=90, radius=1.0, wedgeprops=dict(width=0.3))
    ax.pie(inner_sizes, labels=inner_labels, colors=inner_colors, autopct='%1.1f%%', startangle=90, radius=0.7)

    # Display the chart
    ax.set_title("Nested Pie Chart for Temperature Changes", fontsize=16)
    plt.show()

def consume_sensor_data():
    """Continuously consume sensor data from Kafka."""
    try:
        for message in consumer:
            process_message(message)
    except KeyboardInterrupt:
        print("\n Consumer stopped.")
    finally:
        consumer.close()

if __name__ == "__main__":
    print(f" Listening for messages on Kafka topic: {KAFKA_TOPIC}")

    # Start data consumption in a separate thread
    import threading
    consumer_thread = threading.Thread(target=consume_sensor_data, daemon=True)
    consumer_thread.start()

    # Display the nested pie chart after data consumption
    create_nested_pie_chart()
