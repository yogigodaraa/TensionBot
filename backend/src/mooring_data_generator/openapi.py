"""OpenAPI 3.0 specification generator for mooring data format."""

from typing import Dict, Any


def generate_openapi_spec() -> Dict[str, Any]:
    """Generate OpenAPI 3.0 specification for mooring data."""
    
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Mooring Data API",
            "description": "API specification for mooring sensor data format",
            "version": "1.0.0",
            "contact": {
                "name": "BHP UWA",
                "email": "example@example.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "http://127.0.0.1:8000",
                "description": "Local development server"
            },
            {
                "url": "http://localhost:3000",
                "description": "Dashboard server"
            }
        ],
        "paths": {
            "/api/mooring-data": {
                "post": {
                    "summary": "Receive mooring data",
                    "description": "Endpoint to receive mooring sensor data from data generators",
                    "operationId": "receiveMooringData",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/MooringData"
                                },
                                "example": {
                                    "mooring_id": "MOOR_001",
                                    "location": {
                                        "latitude": -20.7256,
                                        "longitude": 116.8456
                                    },
                                    "timestamp": "2024-11-13T10:30:00.000Z",
                                    "sensors": [
                                        {
                                            "sensor_id": "MOOR_001_SENSOR_01",
                                            "sensor_type": "temperature",
                                            "value": 23.5,
                                            "unit": "°C",
                                            "timestamp": "2024-11-13T10:30:00.000Z",
                                            "quality": "good"
                                        }
                                    ],
                                    "weather": {
                                        "conditions": "partly_cloudy",
                                        "visibility": 15.2,
                                        "humidity": 78.5,
                                        "sea_state": 3,
                                        "swell_height": 1.8,
                                        "swell_period": 9.2
                                    },
                                    "system_status": {
                                        "battery_level": 87.3,
                                        "signal_strength": -65,
                                        "data_transmission_rate": 98.7,
                                        "last_maintenance": "2024-10-15T10:30:00Z",
                                        "operational_days": 87,
                                        "alerts": []
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Data received successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "example": "success"
                                            },
                                            "message": {
                                                "type": "string",
                                                "example": "Mooring data received"
                                            },
                                            "timestamp": {
                                                "type": "string",
                                                "format": "date-time",
                                                "example": "2024-11-13T10:30:00.000Z"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid data format",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        }
                    },
                    "tags": ["Mooring Data"]
                }
            }
        },
        "components": {
            "schemas": {
                "MooringData": {
                    "type": "object",
                    "required": [
                        "mooring_id",
                        "location",
                        "timestamp",
                        "sensors",
                        "weather",
                        "system_status"
                    ],
                    "properties": {
                        "mooring_id": {
                            "type": "string",
                            "description": "Unique identifier for the mooring station",
                            "example": "MOOR_001",
                            "pattern": "^MOOR_[0-9]{3}$"
                        },
                        "location": {
                            "$ref": "#/components/schemas/Location"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "ISO 8601 timestamp when the data was collected",
                            "example": "2024-11-13T10:30:00.000Z"
                        },
                        "sensors": {
                            "type": "array",
                            "description": "Array of sensor readings",
                            "items": {
                                "$ref": "#/components/schemas/SensorReading"
                            },
                            "minItems": 1
                        },
                        "weather": {
                            "$ref": "#/components/schemas/WeatherData"
                        },
                        "system_status": {
                            "$ref": "#/components/schemas/SystemStatus"
                        }
                    }
                },
                "Location": {
                    "type": "object",
                    "required": ["latitude", "longitude"],
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "format": "double",
                            "description": "Latitude in decimal degrees",
                            "minimum": -90,
                            "maximum": 90,
                            "example": -20.7256
                        },
                        "longitude": {
                            "type": "number",
                            "format": "double",
                            "description": "Longitude in decimal degrees",
                            "minimum": -180,
                            "maximum": 180,
                            "example": 116.8456
                        }
                    }
                },
                "SensorReading": {
                    "type": "object",
                    "required": [
                        "sensor_id",
                        "sensor_type",
                        "value",
                        "unit",
                        "timestamp",
                        "quality"
                    ],
                    "properties": {
                        "sensor_id": {
                            "type": "string",
                            "description": "Unique identifier for the sensor",
                            "example": "MOOR_001_SENSOR_01",
                            "pattern": "^MOOR_[0-9]{3}_SENSOR_[0-9]{2}$"
                        },
                        "sensor_type": {
                            "type": "string",
                            "description": "Type of sensor measurement",
                            "enum": [
                                "temperature",
                                "salinity",
                                "pressure",
                                "wave_height",
                                "current_speed",
                                "current_direction",
                                "wind_speed",
                                "wind_direction"
                            ],
                            "example": "temperature"
                        },
                        "value": {
                            "type": "number",
                            "format": "double",
                            "description": "Measured value",
                            "example": 23.5
                        },
                        "unit": {
                            "type": "string",
                            "description": "Unit of measurement",
                            "example": "°C"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "ISO 8601 timestamp when the reading was taken",
                            "example": "2024-11-13T10:30:00.000Z"
                        },
                        "quality": {
                            "type": "string",
                            "description": "Data quality indicator",
                            "enum": ["good", "poor", "questionable"],
                            "example": "good"
                        }
                    }
                },
                "WeatherData": {
                    "type": "object",
                    "required": [
                        "conditions",
                        "visibility",
                        "humidity",
                        "sea_state",
                        "swell_height",
                        "swell_period"
                    ],
                    "properties": {
                        "conditions": {
                            "type": "string",
                            "description": "Current weather conditions",
                            "enum": [
                                "clear",
                                "partly_cloudy",
                                "cloudy",
                                "light_rain",
                                "moderate_rain"
                            ],
                            "example": "partly_cloudy"
                        },
                        "visibility": {
                            "type": "number",
                            "format": "double",
                            "description": "Visibility in kilometers",
                            "minimum": 0,
                            "example": 15.2
                        },
                        "humidity": {
                            "type": "number",
                            "format": "double",
                            "description": "Relative humidity percentage",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 78.5
                        },
                        "sea_state": {
                            "type": "integer",
                            "description": "Sea state on Beaufort scale",
                            "minimum": 0,
                            "maximum": 12,
                            "example": 3
                        },
                        "swell_height": {
                            "type": "number",
                            "format": "double",
                            "description": "Swell height in meters",
                            "minimum": 0,
                            "example": 1.8
                        },
                        "swell_period": {
                            "type": "number",
                            "format": "double",
                            "description": "Swell period in seconds",
                            "minimum": 0,
                            "example": 9.2
                        }
                    }
                },
                "SystemStatus": {
                    "type": "object",
                    "required": [
                        "battery_level",
                        "signal_strength",
                        "data_transmission_rate",
                        "last_maintenance",
                        "operational_days",
                        "alerts"
                    ],
                    "properties": {
                        "battery_level": {
                            "type": "number",
                            "format": "double",
                            "description": "Battery level percentage",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 87.3
                        },
                        "signal_strength": {
                            "type": "integer",
                            "description": "Signal strength in dBm",
                            "minimum": -120,
                            "maximum": 0,
                            "example": -65
                        },
                        "data_transmission_rate": {
                            "type": "number",
                            "format": "double",
                            "description": "Data transmission success rate percentage",
                            "minimum": 0,
                            "maximum": 100,
                            "example": 98.7
                        },
                        "last_maintenance": {
                            "type": "string",
                            "format": "date-time",
                            "description": "ISO 8601 timestamp of last maintenance",
                            "example": "2024-10-15T10:30:00Z"
                        },
                        "operational_days": {
                            "type": "integer",
                            "description": "Days since deployment",
                            "minimum": 0,
                            "example": 87
                        },
                        "alerts": {
                            "type": "array",
                            "description": "System alerts and warnings",
                            "items": {
                                "type": "string"
                            },
                            "example": ["Low battery warning"]
                        }
                    }
                },
                "ErrorResponse": {
                    "type": "object",
                    "required": ["status", "message"],
                    "properties": {
                        "status": {
                            "type": "string",
                            "example": "error"
                        },
                        "message": {
                            "type": "string",
                            "example": "Invalid data format"
                        },
                        "details": {
                            "type": "string",
                            "description": "Additional error details"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2024-11-13T10:30:00.000Z"
                        }
                    }
                }
            }
        },
        "tags": [
            {
                "name": "Mooring Data",
                "description": "Operations related to mooring sensor data"
            }
        ]
    }
    
    return spec