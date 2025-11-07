"""
Model 1: Dự đoán ảnh hưởng của mưa
"""
import numpy as np
import pandas as pd
from config import RAIN_PARAMS
from utils import haversine

def detect_rain_zones(df_weather):
    """
    Phát hiện các vùng mưa từ dữ liệu thời tiết
    """
    df_weather['is_rain_zone'] = (
        (df_weather['Humidity'] > RAIN_PARAMS['humidity_threshold']) & 
        (df_weather['Wind_Speed_kmh'] < RAIN_PARAMS['wind_threshold']) &
        (df_weather['Cloud_Cover'] > RAIN_PARAMS['cloud_threshold'])
    ).astype(int)
    
    rain_zones = df_weather[df_weather['is_rain_zone'] == 1][['latitude', 'longitude']].values
    
    print(f"✓ Phát hiện {len(rain_zones)} vùng mưa")
    return rain_zones

def apply_rain_model(ship_lat, ship_lon, rain_zones):
    """
    Kiểm tra ảnh hưởng mưa đến tàu
    """
    min_rain_dist = float('inf')
    
    for rain_lat, rain_lon in rain_zones:
        dist = haversine(ship_lat, ship_lon, rain_lat, rain_lon)
        if dist < min_rain_dist:
            min_rain_dist = dist
    
    if min_rain_dist < RAIN_PARAMS['radius_km']:
        impact_ratio = 1 - (min_rain_dist / RAIN_PARAMS['radius_km'])
        delay_hours = np.random.uniform(
            RAIN_PARAMS['min_delay_hours'], 
            RAIN_PARAMS['max_delay_hours']
        ) * impact_ratio
        
        return {
            'status': 'Nguy cơ',
            'delay_hours': round(delay_hours, 2),
            'reason': f'Vùng mưa (cách {int(min_rain_dist)}km)',
            'distance_to_hazard': round(min_rain_dist, 1)
        }
    else:
        return {
            'status': 'Đúng giờ',
            'delay_hours': 0.0,
            'reason': 'Thời tiết tốt',
            'distance_to_hazard': None
        }

def predict_rain_impact(ship_df, rain_zones):
    """
    Dự đoán ảnh hưởng mưa cho tất cả tàu
    """
    rain_results = []
    for _, ship in ship_df.iterrows():
        result = apply_rain_model(ship['latitude_ship'], ship['longitude_ship'], rain_zones)
        rain_results.append(result)
    
    rain_df = pd.DataFrame(rain_results)
    ship_df = pd.concat([ship_df.reset_index(drop=True), rain_df], axis=1)
    
    n_risk = len(ship_df[ship_df['status'] == 'Nguy cơ'])
    n_ontime = len(ship_df[ship_df['status'] == 'Đúng giờ'])
    
    print(f"Model 1 hoàn thành:")
    print(f"  - Nguy cơ (mưa): {n_risk} tàu")
    print(f"  - Đúng giờ: {n_ontime} tàu")
    
    return ship_df