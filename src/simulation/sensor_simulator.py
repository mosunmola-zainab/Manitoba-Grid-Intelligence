"""
Sensor Data Simulator for Manitoba Grid Intelligence.

Generates realistic power grid sensor data for development and testing.
"""

import json
import random
import time
from datetime import datetime, timezone
from typing import Generator

from kafka import KafkaProducer


MANITOBA_STATIONS = [
    {"id": "GS-001", "name": "Limestone Generating Station", "type": "hydro", "capacity_mw": 1340},
    {"id": "GS-002", "name": "Kettle Generating Station", "type": "hydro", "capacity_mw": 1220},
    {"id": "GS-003", "name": "Long Spruce Generating Station", "type": "hydro", "capacity_mw": 980},
    {"id": "GS-004", "name": "Grand Rapids Generating Station", "type": "hydro", "capacity_mw": 479},
    {"id": "GS-005", "name": "St. Leon Wind Farm", "type": "wind", "capacity_mw": 99},
    {"id": "GS-006", "name": "St. Joseph Wind Farm", "type": "wind", "capacity_mw": 138},
]

READING_TYPES = [
    {"type": "voltage", "unit": "kV", "base": 230, "variance": 5},
    {"type": "current", "unit": "A", "base": 1000, "variance": 200},
    {"type": "frequency", "unit": "Hz", "base": 60, "variance": 0.1},
    {"type": "power_factor", "unit": "ratio", "base": 0.95, "variance": 0.05},
    {"type": "temperature", "unit": "C", "base": 45, "variance": 15},
]


def generate_sensor_reading(station: dict, reading_type: dict) -> dict:
    """Generate a single sensor reading."""
    value = reading_type["base"] + random.uniform(
        -reading_type["variance"], reading_type["variance"]
    )

    # Simulate occasional anomalies (1% chance)
    quality_flag = 0
    if random.random() < 0.01:
        value *= random.uniform(0.8, 1.2)
        quality_flag = 1

    return {
        "time": datetime.now(timezone.utc).isoformat(),
        "sensor_id": f"{station['id']}-{reading_type['type'].upper()}",
        "station_id": station["id"],
        "station_name": station["name"],
        "reading_type": reading_type["type"],
        "value": round(value, 4),
        "unit": reading_type["unit"],
        "quality_flag": quality_flag,
    }


def generate_power_reading(station: dict) -> dict:
    """Generate power generation reading for a station."""
    # Hydro stations operate at higher capacity factors
    if station["type"] == "hydro":
        capacity_factor = random.uniform(0.7, 0.95)
    else:  # wind
        capacity_factor = random.uniform(0.2, 0.45)

    generation_mw = station["capacity_mw"] * capacity_factor

    return {
        "time": datetime.now(timezone.utc).isoformat(),
        "station_id": station["id"],
        "station_name": station["name"],
        "station_type": station["type"],
        "generation_mw": round(generation_mw, 2),
        "capacity_mw": station["capacity_mw"],
        "capacity_factor": round(capacity_factor, 4),
    }


def stream_sensor_data(
    bootstrap_servers: str = "localhost:9094",
    topic: str = "grid.sensor.readings",
    interval_seconds: float = 1.0,
) -> Generator[dict, None, None]:
    """Stream simulated sensor data to Kafka."""
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    print(f"Starting sensor simulator - publishing to {topic}")

    try:
        while True:
            for station in MANITOBA_STATIONS:
                # Generate sensor readings
                for reading_type in READING_TYPES:
                    reading = generate_sensor_reading(station, reading_type)
                    producer.send(topic, value=reading)
                    yield reading

                # Generate power reading
                power_reading = generate_power_reading(station)
                producer.send("grid.power.generation", value=power_reading)
                yield power_reading

            producer.flush()
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("Shutting down simulator...")
    finally:
        producer.close()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")

    for reading in stream_sensor_data(bootstrap_servers=bootstrap_servers):
        print(f"Published: {reading['sensor_id'] if 'sensor_id' in reading else reading['station_id']}")
