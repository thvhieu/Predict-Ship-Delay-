"""
Model 2: Dự đoán ảnh hưởng của bão
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from config import STORM_PARAMS
from utils import haversine, classify_storm_level

def detect_storm_centers(df_weather):
    """
    Sử dụng clustering để phát hiện tâm bão
    """
    features_storm = ['latitude', 'longitude', 'Wind_Speed_kmh', 
                      'significant_wave_height', 'Pressure']
    X_storm = df_weather[features_storm].fillna(df_weather[features_storm].mean())
    
    scaler_storm = StandardScaler()
    X_storm_scaled = scaler_storm.fit_transform(X_storm)
    
    kmeans = KMeans(n_clusters=STORM_PARAMS['n_clusters'], random_state=42, n_init=20)
    df_weather['storm_cluster'] = kmeans.fit_predict(X_storm_scaled)
    
    # Xác định thông tin từng bão
    storms = []
    for i in range(STORM_PARAMS['n_clusters']):
        cluster = df_weather[df_weather['storm_cluster'] == i]
        
        lat = cluster['latitude'].mean()
        lon = cluster['longitude'].mean()
        wind = cluster['Wind_Speed_kmh'].mean()
        wave = cluster['significant_wave_height'].mean()
        pressure = cluster['Pressure'].mean()
        
        # Tính bán kính bão
        radius_km = (STORM_PARAMS['base_radius'] + 
                     wind * STORM_PARAMS['wind_factor'] + 
                     wave * STORM_PARAMS['wave_factor'])
        
        warning_radius_km = radius_km * STORM_PARAMS['warning_multiplier']
        
        level = classify_storm_level(wind)
        
        storms.append({
            'storm_id': i,
            'name': f"Storm_{i+1}",
            'latitude': round(lat, 2),
            'longitude': round(lon, 2),
            'wind_kmh': round(wind, 1),
            'level': level,
            'radius_km': round(radius_km, 1),
            'warning_radius_km': round(warning_radius_km, 1)
        })
    
    storm_df = pd.DataFrame(storms)
    
    print(f"✓ Phát hiện {len(storms)} tâm bão:")
    for _, s in storm_df.iterrows():
        print(f"  {s['name']}: {s['level']} - Gió {s['wind_kmh']} km/h")
        print(f"  Tâm: ({s['latitude']}°N, {s['longitude']}°E)")
        print(f"  Bán kính nguy hiểm: {s['radius_km']} km")
    
    return storm_df, df_weather

def apply_storm_model(ship_lat, ship_lon, storms_df):
    """
    Kiểm tra ảnh hưởng bão đến tàu
    """
    min_storm_dist = float('inf')
    closest_storm = None
    
    for _, storm in storms_df.iterrows():
        dist = haversine(ship_lat, ship_lon, storm['latitude'], storm['longitude'])
        if dist < min_storm_dist:
            min_storm_dist = dist
            closest_storm = storm
    
    if closest_storm is not None:
        # TRONG VÙNG NGUY HIỂM
        if min_storm_dist < closest_storm['radius_km']:
            impact_ratio = 1 - (min_storm_dist / closest_storm['radius_km'])
            delay_hours = np.random.uniform(
                STORM_PARAMS['danger_min_delay'], 
                STORM_PARAMS['danger_max_delay']
            ) * impact_ratio
            
            return {
                'status': 'Trễ',
                'delay_hours': round(delay_hours, 2),
                'reason': f"Bão {closest_storm['name']} ({closest_storm['level']})",
                'distance_to_hazard': round(min_storm_dist, 1),
                'override': True
            }
        
        # TRONG VÙNG CẢNH BÁO
        elif min_storm_dist < closest_storm['warning_radius_km']:
            impact_ratio = 1 - (min_storm_dist / closest_storm['warning_radius_km'])
            delay_hours = np.random.uniform(
                STORM_PARAMS['warning_min_delay'], 
                STORM_PARAMS['warning_max_delay']
            ) * impact_ratio
            
            return {
                'status': 'Nguy cơ',
                'delay_hours': round(delay_hours, 2),
                'reason': f"Gần bão {closest_storm['name']} (cách {int(min_storm_dist)}km)",
                'distance_to_hazard': round(min_storm_dist, 1),
                'override': True
            }
    
    # XA BÃO
    return {
        'status': None,
        'delay_hours': None,
        'reason': None,
        'distance_to_hazard': None,
        'override': False
    }

def predict_storm_impact(ship_df, storm_df):
    """
    Dự đoán ảnh hưởng bão cho tất cả tàu (override model mưa nếu cần)
    """
    storm_override_count = 0
    
    for idx, ship in ship_df.iterrows():
        storm_result = apply_storm_model(
            ship['latitude_ship'], 
            ship['longitude_ship'], 
            storm_df
        )
        
        if storm_result['override']:
            ship_df.at[idx, 'status'] = storm_result['status']
            ship_df.at[idx, 'delay_hours'] = storm_result['delay_hours']
            ship_df.at[idx, 'reason'] = storm_result['reason']
            ship_df.at[idx, 'distance_to_hazard'] = storm_result['distance_to_hazard']
            storm_override_count += 1
    
    print(f"✓ Model 2 hoàn thành:")
    print(f"  - Override: {storm_override_count} tàu bị ảnh hưởng bão")
    
    return ship_df