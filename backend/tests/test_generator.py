"""Tests for mooring data generator."""

import json
from unittest.mock import MagicMock, patch

from mooring_data_generator.cli import MooringDataFileWriter, MooringDataSender
from mooring_data_generator.generator import MooringDataGenerator, SensorReading


def test_sensor_reading_creation():
    """Test SensorReading dataclass creation."""
    reading = SensorReading(
        sensor_id="TEST_01",
        sensor_type="temperature",
        value=23.5,
        unit="°C",
        timestamp="2024-11-13T10:30:00.000Z"
    )

    assert reading.sensor_id == "TEST_01"
    assert reading.sensor_type == "temperature"
    assert reading.value == 23.5
    assert reading.unit == "°C"
    assert reading.quality == "good"  # default value


def test_mooring_data_generator():
    """Test MooringDataGenerator functionality."""
    generator = MooringDataGenerator("TEST_MOOR")

    # Test data generation
    data = generator.generate_data()
    assert data.mooring_id == "TEST_MOOR"
    assert len(data.sensors) == 8  # Should have 8 sensor types
    assert "latitude" in data.location
    assert "longitude" in data.location

    # Test JSON generation
    json_data = generator.generate_json()
    parsed = json.loads(json_data)
    assert parsed["mooring_id"] == "TEST_MOOR"

    # Test dict generation
    dict_data = generator.generate_dict()
    assert dict_data["mooring_id"] == "TEST_MOOR"
    assert isinstance(dict_data["sensors"], list)


def test_sensor_drift():
    """Test that sensor values drift realistically."""
    generator = MooringDataGenerator("TEST_MOOR")

    # Generate multiple readings
    readings = []
    for _ in range(10):
        data = generator.generate_data()
        temp_sensor = next(s for s in data.sensors if s.sensor_type == "temperature")
        readings.append(temp_sensor.value)

    # Values should be different (drift) but within reasonable bounds
    assert len(set(readings)) > 1  # Should have some variation
    assert all(18.0 <= reading <= 28.0 for reading in readings)


@patch('requests.Session.post')
def test_mooring_data_sender(mock_post):
    """Test HTTP data sender."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    sender = MooringDataSender("http://test.com/api")
    test_data = {"test": "data"}

    result = sender.send_data(test_data)
    assert result is True
    assert sender.success_count == 1
    assert sender.error_count == 0

    mock_post.assert_called_once()


def test_mooring_data_file_writer(tmp_path):
    """Test file writer functionality."""
    test_file = tmp_path / "test_output.json"

    with MooringDataFileWriter(str(test_file)) as writer:
        test_data1 = {"mooring_id": "MOOR_001", "timestamp": "2024-11-13T10:30:00Z"}
        test_data2 = {"mooring_id": "MOOR_002", "timestamp": "2024-11-13T10:31:00Z"}

        writer.write_data(test_data1)
        writer.write_data(test_data2)

    # Verify file contents
    with open(test_file) as f:
        content = f.read()
        data = json.loads(content)

    assert len(data) == 2
    assert data[0]["mooring_id"] == "MOOR_001"
    assert data[1]["mooring_id"] == "MOOR_002"


def test_generator_sensor_types():
    """Test that all expected sensor types are generated."""
    generator = MooringDataGenerator()
    data = generator.generate_data()

    sensor_types = {sensor.sensor_type for sensor in data.sensors}
    expected_types = {
        "temperature", "salinity", "pressure", "wave_height",
        "current_speed", "current_direction", "wind_speed", "wind_direction"
    }

    assert sensor_types == expected_types


def test_weather_data_generation():
    """Test weather data generation."""
    generator = MooringDataGenerator()
    data = generator.generate_data()
    weather = data.weather

    assert "conditions" in weather
    assert weather["conditions"] in [
        "clear",
        "partly_cloudy",
        "cloudy",
        "light_rain",
        "moderate_rain",
    ]
    assert 0 <= weather["visibility"] <= 20
    assert 0 <= weather["humidity"] <= 100
    assert 1 <= weather["sea_state"] <= 6


def test_system_status_generation():
    """Test system status generation."""
    generator = MooringDataGenerator()
    data = generator.generate_data()
    status = data.system_status

    assert 0 <= status["battery_level"] <= 100
    assert -120 <= status["signal_strength"] <= 0
    assert 0 <= status["data_transmission_rate"] <= 100
    assert isinstance(status["operational_days"], int)
    assert isinstance(status["alerts"], list)
