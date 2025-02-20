import json
import time
import random
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kafka Configurations
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sensor_data")

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_sensor_data():
    """Generate random sensor readings for vibration, temperature, and sound level."""
    return {
        "timestamp": int(time.time()),  # Current time in UNIX format
        "vibration": round(random.uniform(0.5, 10.0), 2),  # Vibration in mm/s
        "temperature": round(random.uniform(20.0, 100.0), 2),  # Temperature in °C
        "sound_level": round(random.uniform(50.0, 120.0), 2)  # Sound level in dB
    }

def produce_sensor_data():
    """Continuously produce and send sensor data to Kafka."""
    try:
        while True:
            sensor_data = generate_sensor_data()
            producer.send(KAFKA_TOPIC, value=sensor_data)
            print(f"📤 Sent: {sensor_data}")
            time.sleep(2)  # Simulate a delay in real-time streaming
    except KeyboardInterrupt:
        print("\n⏹ Producer stopped.")
    finally:
        producer.close()

if __name__ == "__main__":
    print(f"🚀 Streaming sensor data to Kafka topic: {KAFKA_TOPIC}")
    produce_sensor_data()
