import json
import os
import time
from collections import deque
from kafka import KafkaConsumer
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dotenv import load_dotenv
from utils.alert_utils import send_sms_alert

# Load environment variables
load_dotenv()

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
    timestamps.append(sensor_data["timestamp"])
    vibrations.append(sensor_data["vibration"])
    temperatures.append(sensor_data["temperature"])
    sound_levels.append(sensor_data["sound_level"])

    check_anomalies(sensor_data)

def update_plot(frame, ax1, ax2, ax3):
    """Update the Matplotlib live plot with new data."""
    ax1.clear()
    ax2.clear()
    ax3.clear()

    ax1.plot(timestamps, vibrations, "b-", label="Vibration (mm/s)")
    ax2.plot(timestamps, temperatures, "r-", label="Temperature (°C)")
    ax3.plot(timestamps, sound_levels, "g-", label="Sound Level (dB)")

    # Set titles and labels
    ax1.set_title("Vibration Over Time")
    ax2.set_title("Temperature Over Time")
    ax3.set_title("Sound Level Over Time")

    for ax in [ax1, ax2, ax3]:
        ax.set_xlabel("Time")
        ax.legend()
        ax.grid()

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

    # Set up live visualization
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
    ani = animation.FuncAnimation(fig, update_plot, fargs=(ax1, ax2, ax3), interval=1000)
    plt.show()
