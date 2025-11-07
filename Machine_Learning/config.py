"""
Configuration file cho hệ thống dự đoán ETA
"""

# ===== MYSQL CONFIGURATION =====
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'shipping_ml'
}

# ===== FILE PATHS =====
DATA_PATHS = {
    'weather': 'weather_data_asia.csv',
    'weather_rain': 'weather_rain_clean1.csv',
    'wave': 'wave_clean1.csv',
    'ship': 'danh_sach_tau_100.csv',
    'ports': 'cang_bien_chau_a_14.csv'
}

# ===== OUTPUT PATHS =====
OUTPUT_PATHS = {
    'eta_report': 'ship_eta_report.csv',
    'storm_info': 'storm_info.csv',
    'weather_combined': 'weather_combined.csv'
}

# ===== MODEL PARAMETERS =====
RAIN_PARAMS = {
    'radius_km': 250,
    'min_delay_hours': 1.0,
    'max_delay_hours': 3.0,
    'humidity_threshold': 70,
    'wind_threshold': 120,
    'cloud_threshold': 60
}

STORM_PARAMS = {
    'n_clusters': 8,
    'base_radius': 200,
    'wind_factor': 3.5,
    'wave_factor': 35,
    'warning_multiplier': 1.5,
    'danger_min_delay': 6.0,
    'danger_max_delay': 24.0,
    'warning_min_delay': 1.0,
    'warning_max_delay': 3.0
}

# ===== STORM CENTERS =====
STORM_CENTERS = [
    {'lat': 15.2, 'lon': 115.3, 'wind': 165, 'pressure': 935, 'wave': 7.5, 'name': 'Biển Đông Nam'},
    {'lat': 22.5, 'lon': 120.8, 'wind': 148, 'pressure': 952, 'wave': 6.8, 'name': 'Đài Loan'},
    {'lat': 10.8, 'lon': 108.2, 'wind': 135, 'pressure': 962, 'wave': 6.2, 'name': 'Vũng Tàu'},
    {'lat': 35.2, 'lon': 129.5, 'wind': 125, 'pressure': 968, 'wave': 5.5, 'name': 'Busan'},
    {'lat': 13.5, 'lon': 80.8, 'wind': 115, 'pressure': 973, 'wave': 5.0, 'name': 'Chennai'},
    {'lat': 25.0, 'lon': 105.0, 'wind': 140, 'pressure': 945, 'wave': 6.5, 'name': 'Vịnh Bắc Bộ'},
    {'lat': 18.0, 'lon': 112.0, 'wind': 155, 'pressure': 940, 'wave': 7.0, 'name': 'Hoàng Sa'},
    {'lat': 30.0, 'lon': 125.0, 'wind': 130, 'pressure': 960, 'wave': 6.0, 'name': 'Hàn Quốc'}
]

# ===== REQUIRED COLUMNS =====
REQUIRED_WEATHER_COLS = [
    'Temperature', 'Humidity', 'Wind_Speed_kmh', 'Cloud_Cover',
    'Pressure', 'significant_wave_height', 'latitude', 'longitude'
]

SHIP_COLS_MAPPING = {
    0: 'ship_name',
    1: 'IMO',
    2: 'port_from',
    3: 'time_from',
    4: 'port_to',
    5: 'time_to',
    6: 'latitude_ship',
    7: 'longitude_ship'
}