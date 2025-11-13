"""Mooring data generation module."""

import json
import random
import time
from datetime import datetime, timezone
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class SensorReading:
    """Individual sensor reading."""
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    quality: str = "good"


@dataclass
class MooringData:
    """Complete mooring data payload."""
    mooring_id: str
    location: Dict[str, float]
    timestamp: str
    sensors: List[SensorReading]
    weather: Dict[str, Any]
    system_status: Dict[str, Any]


class MooringDataGenerator:
    """Generate realistic mooring data."""
    
    def __init__(self, mooring_id: str = "MOOR_001"):
        self.mooring_id = mooring_id
        self.location = {
            "latitude": -20.7256 + random.uniform(-0.01, 0.01),
            "longitude": 116.8456 + random.uniform(-0.01, 0.01)
        }
        
        # Sensor configuration
        self.sensors_config = {
            "temperature": {"min": 18.0, "max": 28.0, "unit": "°C", "drift": 0.1},
            "salinity": {"min": 34.5, "max": 35.5, "unit": "PSU", "drift": 0.05},
            "pressure": {"min": 1010.0, "max": 1025.0, "unit": "hPa", "drift": 0.5},
            "wave_height": {"min": 0.5, "max": 4.0, "unit": "m", "drift": 0.2},
            "current_speed": {"min": 0.1, "max": 2.5, "unit": "m/s", "drift": 0.1},
            "current_direction": {"min": 0, "max": 360, "unit": "degrees", "drift": 5},
            "wind_speed": {"min": 0.0, "max": 15.0, "unit": "m/s", "drift": 0.3},
            "wind_direction": {"min": 0, "max": 360, "unit": "degrees", "drift": 10},
        }
        
        # Initialize sensor states for realistic drift
        self.sensor_states = {}
        for sensor, config in self.sensors_config.items():
            self.sensor_states[sensor] = random.uniform(config["min"], config["max"])
    
    def _generate_sensor_reading(self, sensor_type: str, sensor_id: str) -> SensorReading:
        """Generate a single sensor reading with realistic drift."""
        config = self.sensors_config[sensor_type]
        
        # Apply random drift
        drift = random.uniform(-config["drift"], config["drift"])
        self.sensor_states[sensor_type] += drift
        
        # Keep within realistic bounds
        self.sensor_states[sensor_type] = max(
            config["min"], 
            min(config["max"], self.sensor_states[sensor_type])
        )
        
        # Add some random noise
        noise = random.uniform(-config["drift"] * 0.1, config["drift"] * 0.1)
        value = self.sensor_states[sensor_type] + noise
        
        # Occasionally simulate sensor issues
        quality = "good"
        if random.random() < 0.02:  # 2% chance of sensor issue
            quality = random.choice(["poor", "questionable"])
            value *= random.uniform(0.8, 1.2)
        
        return SensorReading(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            value=round(value, 2),
            unit=config["unit"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            quality=quality
        )
    
    def _generate_weather_data(self) -> Dict[str, Any]:
        """Generate weather conditions."""
        return {
            "conditions": random.choice([
                "clear", "partly_cloudy", "cloudy", "light_rain", "moderate_rain"
            ]),
            "visibility": round(random.uniform(5.0, 20.0), 1),
            "humidity": round(random.uniform(60, 90), 1),
            "sea_state": random.randint(1, 6),
            "swell_height": round(random.uniform(0.5, 3.0), 1),
            "swell_period": round(random.uniform(6, 14), 1)
        }
    
    def _generate_system_status(self) -> Dict[str, Any]:
        """Generate system status information."""
        return {
            "battery_level": round(random.uniform(75, 100), 1),
            "signal_strength": random.randint(-80, -40),
            "data_transmission_rate": round(random.uniform(95.0, 99.9), 1),
            "last_maintenance": "2024-10-15T10:30:00Z",
            "operational_days": random.randint(45, 120),
            "alerts": [] if random.random() > 0.1 else [
                random.choice([
                    "Low battery warning",
                    "Sensor calibration due",
                    "High wave conditions"
                ])
            ]
        }
    
    def generate_data(self) -> MooringData:
        """Generate a complete mooring data payload."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Generate sensor readings
        sensors = []
        for i, (sensor_type, _) in enumerate(self.sensors_config.items()):
            sensor_id = f"{self.mooring_id}_SENSOR_{i+1:02d}"
            sensors.append(self._generate_sensor_reading(sensor_type, sensor_id))
        
        return MooringData(
            mooring_id=self.mooring_id,
            location=self.location,
            timestamp=timestamp,
            sensors=sensors,
            weather=self._generate_weather_data(),
            system_status=self._generate_system_status()
        )
    
    def generate_json(self) -> str:
        """Generate mooring data as JSON string."""
        data = self.generate_data()
        return json.dumps(asdict(data), indent=2)
    
    def generate_dict(self) -> Dict[str, Any]:
        """Generate mooring data as dictionary."""
        data = self.generate_data()
        return asdict(data)