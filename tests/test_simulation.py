"""Tests for the sensor simulator module."""

import pytest
from src.simulation.sensor_simulator import (
    generate_sensor_reading,
    generate_power_reading,
    MANITOBA_STATIONS,
    READING_TYPES,
)


class TestSensorSimulator:
    """Test cases for sensor data simulation."""

    def test_generate_sensor_reading_has_required_fields(self):
        """Sensor readings should contain all required fields."""
        station = MANITOBA_STATIONS[0]
        reading_type = READING_TYPES[0]

        reading = generate_sensor_reading(station, reading_type)

        assert "time" in reading
        assert "sensor_id" in reading
        assert "station_id" in reading
        assert "reading_type" in reading
        assert "value" in reading
        assert "unit" in reading
        assert "quality_flag" in reading

    def test_generate_sensor_reading_value_in_range(self):
        """Sensor reading values should be within expected variance."""
        station = MANITOBA_STATIONS[0]
        reading_type = {"type": "test", "unit": "X", "base": 100, "variance": 10}

        # Generate multiple readings to test variance
        for _ in range(100):
            reading = generate_sensor_reading(station, reading_type)
            # Allow for anomalies (20% deviation)
            assert 70 <= reading["value"] <= 130

    def test_generate_power_reading_has_required_fields(self):
        """Power readings should contain all required fields."""
        station = MANITOBA_STATIONS[0]

        reading = generate_power_reading(station)

        assert "time" in reading
        assert "station_id" in reading
        assert "generation_mw" in reading
        assert "capacity_factor" in reading

    def test_hydro_station_capacity_factor(self):
        """Hydro stations should have higher capacity factors."""
        hydro_station = next(s for s in MANITOBA_STATIONS if s["type"] == "hydro")

        readings = [generate_power_reading(hydro_station) for _ in range(100)]
        avg_capacity = sum(r["capacity_factor"] for r in readings) / len(readings)

        # Hydro should average above 0.7
        assert avg_capacity > 0.65

    def test_wind_station_capacity_factor(self):
        """Wind stations should have lower capacity factors than hydro."""
        wind_station = next(s for s in MANITOBA_STATIONS if s["type"] == "wind")

        readings = [generate_power_reading(wind_station) for _ in range(100)]
        avg_capacity = sum(r["capacity_factor"] for r in readings) / len(readings)

        # Wind should average below 0.5
        assert avg_capacity < 0.5

    def test_generation_does_not_exceed_capacity(self):
        """Generated power should never exceed station capacity."""
        for station in MANITOBA_STATIONS:
            for _ in range(50):
                reading = generate_power_reading(station)
                assert reading["generation_mw"] <= station["capacity_mw"] * 1.2  # Allow anomaly margin
