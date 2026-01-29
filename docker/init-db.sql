-- Initialize TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create Airflow database and user
CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

-- Create schemas for the grid intelligence platform
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create hypertable for sensor readings
CREATE TABLE IF NOT EXISTS raw.sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    sensor_id VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    reading_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION,
    unit VARCHAR(20),
    quality_flag INTEGER DEFAULT 0
);

SELECT create_hypertable('raw.sensor_readings', 'time', if_not_exists => TRUE);

-- Create index for common queries
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_id ON raw.sensor_readings (sensor_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_type ON raw.sensor_readings (reading_type, time DESC);

-- Create table for grid stations
CREATE TABLE IF NOT EXISTS raw.grid_stations (
    station_id VARCHAR(50) PRIMARY KEY,
    station_name VARCHAR(200),
    station_type VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    capacity_mw DOUBLE PRECISION,
    region VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create table for power generation data
CREATE TABLE IF NOT EXISTS raw.power_generation (
    time TIMESTAMPTZ NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    generation_mw DOUBLE PRECISION,
    capacity_factor DOUBLE PRECISION,
    fuel_type VARCHAR(50),
    emissions_tons DOUBLE PRECISION
);

SELECT create_hypertable('raw.power_generation', 'time', if_not_exists => TRUE);

-- Create table for demand data
CREATE TABLE IF NOT EXISTS raw.power_demand (
    time TIMESTAMPTZ NOT NULL,
    region VARCHAR(100) NOT NULL,
    demand_mw DOUBLE PRECISION,
    temperature_c DOUBLE PRECISION,
    forecast_demand_mw DOUBLE PRECISION
);

SELECT create_hypertable('raw.power_demand', 'time', if_not_exists => TRUE);

-- Grant permissions
GRANT ALL ON SCHEMA raw TO grid_user;
GRANT ALL ON SCHEMA staging TO grid_user;
GRANT ALL ON SCHEMA analytics TO grid_user;
GRANT ALL ON ALL TABLES IN SCHEMA raw TO grid_user;
GRANT ALL ON ALL TABLES IN SCHEMA staging TO grid_user;
GRANT ALL ON ALL TABLES IN SCHEMA analytics TO grid_user;
