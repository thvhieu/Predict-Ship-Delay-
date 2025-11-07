CREATE DATABASE shipping_ml;

USE shipping_ml;

-- Bảng kết quả ETA (đã bỏ created_at và thêm latitude/longitude)
CREATE TABLE eta_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ship_name VARCHAR(100),
    port_from VARCHAR(100),
    port_to VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    eta_expected DATETIME,
    delay_hours FLOAT,
    status VARCHAR(50),
    reason TEXT,
    distance_to_hazard FLOAT
);

-- Bảng thông tin bão
CREATE TABLE storm_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    storm_id INT,
    name VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    wind_kmh FLOAT,
    level VARCHAR(50),
    radius_km FLOAT,
    warning_radius_km FLOAT,
);

-- Bảng dữ liệu thời tiết
CREATE TABLE weather_combined (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed_kmh FLOAT,
    cloud_cover FLOAT,
    pressure FLOAT,
    significant_wave_height FLOAT,
    mean_wave_period FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    is_rain_zone INT,
    storm_cluster INT,
);

-- Bảng cảng biển
CREATE TABLE sea_ports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(100),
    port_name VARCHAR(100),
    country VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    status VARCHAR(50),
);