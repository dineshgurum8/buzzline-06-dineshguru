import json
import os
import time
from collections import deque
from kafka import KafkaConsumer
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
from dotenv import load_dotenv
from utils.alert_utils import send_sms_alert
import numpy as np

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

    # Set titles and labels for line plots
    ax1.set_title("Vibration Over Time")
    ax2.set_title("Temperature Over Time")
    ax3.set_title("Sound Level Over Time")

    for ax in [ax1, ax2, ax3]:
        ax.set_xlabel("Time")
        ax.legend()
        ax.grid()

def temperature_dial_plot():
    """Plot a single Temperature Dial Gauge showing Low, Medium, and High ranges."""
    temp = temperatures[-1] if temperatures else 0  # Get the latest temperature

    # Define temperature ranges
    low_range = (0, 60)
    medium_range = (60, 120)
    high_range = (120, 180)

    # Create a single polar plot
    fig, ax = plt.subplots(figsize=(25, 25), subplot_kw={'projection': 'polar'})

    # Set up the polar plot
    ax.set_theta_zero_location('N')  # 0 degrees at the top
    ax.set_theta_direction(-1)  # Clockwise direction
    ax.set_theta_offset(np.pi)
    ax.set_ylim(0, 1)  # Radial limits

    # Draw the gauge background
    theta = np.linspace(0, np.pi, 100)
    r = np.ones_like(theta) * 0.5
    ax.plot(theta, r, color='gray', lw=3, alpha=0.4)

    # Draw the colored ranges for Low, Medium, and High temperatures
    low_theta = np.linspace(0, np.pi * (low_range[1] / 180), 100)
    medium_theta = np.linspace(np.pi * (medium_range[0] / 180), np.pi * (medium_range[1] / 180), 100)
    high_theta = np.linspace(np.pi * (high_range[0] / 180), np.pi * (high_range[1] / 180), 100)

    ax.fill_between(low_theta, 0, 0.5, color='green', alpha=0.5, label='Low Temp (0-60°C)')
    ax.fill_between(medium_theta, 0, 0.5, color='orange', alpha=0.5, label='Medium Temp (60-120°C)')
    ax.fill_between(high_theta, 0, 0.5, color='red', alpha=0.5, label='High Temp (120-180°C)')

    # Draw the pointer for the current temperature
    temp_angle = (temp / 180) * np.pi  # Convert temperature to angle
    ax.plot([temp_angle, temp_angle], [0, 0.5], color='black', lw=2, label=f'Current Temp: {temp}°C')

    # Add a label in the center of the dial
    ax.text(0, 0.3, f"{temp}°C", horizontalalignment='center', verticalalignment='center', fontsize=16, fontweight='bold')

    # Add a legend
    ax.legend(loc='center left', bbox_to_anchor=(1.1, 1.1))

    # Hide radial ticks
    ax.set_rticks([])

    # Set title
    ax.set_title("Condition Monitoring -Temperature Gauge", fontsize=16, pad=20)
    ax.set_axis_off()

    plt.tight_layout()
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

    # Set up live visualization with a corrected layout for line plots
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # Assign the axes to the plots
    ax1, ax2, ax3 = axs[0], axs[1], axs[2]  # Assigning axes to each plot

    ani = animation.FuncAnimation(fig, update_plot, fargs=(ax1, ax2, ax3), interval=1000)

    plt.tight_layout()
    plt.show()

    # Show the separate temperature dial plot
    temperature_dial_plot()
