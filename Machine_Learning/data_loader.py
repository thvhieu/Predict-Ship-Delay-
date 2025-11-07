"""
Module load và xử lý dữ liệu
"""
import pandas as pd
import numpy as np
from config import DATA_PATHS, REQUIRED_WEATHER_COLS, SHIP_COLS_MAPPING, STORM_CENTERS

def load_weather_data():
    """Load và kết hợp dữ liệu thời tiết"""
    try:
        df_weather = pd.read_csv(DATA_PATHS['weather'])
        print("✓ Đã load weather_data_asia.csv")
    except:
        print("! Không tìm thấy weather_data_asia.csv, dùng dữ liệu mưa")
        rain_df = pd.read_csv(DATA_PATHS['weather_rain'])
        np.random.seed(42)
        rain_df['latitude'] = np.random.uniform(0, 45, len(rain_df))
        rain_df['longitude'] = np.random.uniform(90, 140, len(rain_df))
        rain_df['Wind_Speed_kmh'] = rain_df['Wind_Speed'] * 10
        df_weather = rain_df

    # Load wave data
    try:
        wave_df = pd.read_csv(DATA_PATHS['wave'])
        if len(wave_df) >= len(df_weather):
            df_weather['significant_wave_height'] = wave_df['significant_wave_height'].iloc[:len(df_weather)].values
            df_weather['mean_wave_period'] = wave_df['mean_wave_period'].iloc[:len(df_weather)].values
        print("✓ Đã load wave_clean1.csv")
    except:
        print("! Không tìm thấy wave_clean1.csv, tạo dữ liệu ngẫu nhiên")
        df_weather['significant_wave_height'] = np.random.uniform(1, 8, len(df_weather))
        df_weather['mean_wave_period'] = np.random.uniform(5, 10, len(df_weather))

    # Đảm bảo các cột cần thiết
    for col in REQUIRED_WEATHER_COLS:
        if col not in df_weather.columns:
            if col == 'Wind_Speed_kmh' and 'Wind_Speed' in df_weather.columns:
                df_weather['Wind_Speed_kmh'] = df_weather['Wind_Speed'] * 10
            else:
                df_weather[col] = 0

    return df_weather

def augment_storm_data(df_weather):
    """Tăng cường dữ liệu bão"""
    for i, center in enumerate(STORM_CENTERS):
        start = i * 12
        end = start + 12
        if end <= len(df_weather):
            df_weather.loc[start:end-1, 'latitude'] = np.random.normal(center['lat'], 2.0, 12)
            df_weather.loc[start:end-1, 'longitude'] = np.random.normal(center['lon'], 2.0, 12)
            df_weather.loc[start:end-1, 'Wind_Speed_kmh'] = np.random.normal(center['wind'], 15, 12)
            df_weather.loc[start:end-1, 'Pressure'] = np.random.normal(center['pressure'], 8, 12)
            df_weather.loc[start:end-1, 'significant_wave_height'] = np.random.normal(center['wave'], 0.8, 12)
    
    print(f"✓ Đã tăng cường {len(STORM_CENTERS)} tâm bão")
    return df_weather

def load_ship_data():
    """Load dữ liệu tàu"""
    ship_df = pd.read_csv(DATA_PATHS['ship'])
    ship_df.columns = list(SHIP_COLS_MAPPING.values())
    
    # Xử lý tọa độ
    for col in ['latitude_ship', 'longitude_ship']:
        ship_df[col] = pd.to_numeric(ship_df[col], errors='coerce')
    ship_df = ship_df.dropna(subset=['latitude_ship', 'longitude_ship'])
    
    # Xử lý thời gian
    ship_df['ETA'] = pd.to_datetime(ship_df['time_to'])
    
    print(f"✓ Đã load {len(ship_df)} tàu")
    return ship_df

def load_port_data():
    """Load dữ liệu cảng biển"""
    try:
        df_ports = pd.read_csv(DATA_PATHS['ports'])
        port_cols_map = {
            "Vùng biển": "region",
            "Tên cảng": "port_name",
            "Quốc gia": "country",
            "Vĩ độ": "latitude",
            "Kinh độ": "longitude",
            "Trạng thái": "status"
        }
        df_ports = df_ports.rename(columns=port_cols_map)
        print(f"✓ Đã load {len(df_ports)} cảng biển")
        return df_ports
    except Exception as e:
        print(f"! Không load được dữ liệu cảng: {e}")
        return None