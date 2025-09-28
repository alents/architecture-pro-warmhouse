-- Create the database if it doesn't exist
CREATE DATABASE smarthome;

-- Connect to the database
\c smarthome;

-- Create the sensors table
CREATE TABLE IF NOT EXISTS sensors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    value FLOAT DEFAULT 0,
    unit VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'inactive',
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create the telemetry table
CREATE TABLE IF NOT EXISTS telemetry (
    sensor_id INTEGER NOT NULL,
    value FLOAT NOT NULL,
    value_timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);


-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sensors_type ON sensors(type);
CREATE INDEX IF NOT EXISTS idx_sensors_location ON sensors(location);
CREATE INDEX IF NOT EXISTS idx_sensors_status ON sensors(status);
CREATE INDEX IF NOT EXISTS idx_telemetry_value_timestamp ON telemetry(value_timestamp);

INSERT INTO sensors (name, type, location, unit) VALUES ('Living Room Temperature', 'temperature', 'Living Room', '°C');
INSERT INTO sensors (name, type, location, unit) VALUES ('Kitchen Temperature', 'temperature', 'Kitchen', '°C');
INSERT INTO sensors (name, type, location, unit) VALUES ('Bedroom Temperature', 'temperature', 'Bedroom', '°C');