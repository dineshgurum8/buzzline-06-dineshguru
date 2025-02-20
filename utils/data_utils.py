import json
import os
from jsonschema import validate, ValidationError

# Define expected sensor data schema
SENSOR_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "timestamp": {"type": "integer"},
        "vibration": {"type": "number"},
        "temperature": {"type": "number"},
        "sound_level": {"type": "number"}
    },
    "required": ["timestamp", "vibration", "temperature", "sound_level"]
}

def load_json_data(file_path):
    """Load sensor data from a JSON file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"⚠ Error loading JSON file: {e}")
        return []

def validate_sensor_data(data):
    """Validate sensor data against predefined schema."""
    try:
        validate(instance=data, schema=SENSOR_DATA_SCHEMA)
        return True
    except ValidationError as e:
        print(f"⚠ Invalid data: {e}")
        return False
