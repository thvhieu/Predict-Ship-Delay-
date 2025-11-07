"""
Module load dữ liệu vào MySQL
"""
import numpy as np
import pandas as pd
import mysql.connector
from mysql.connector import Error
from config import MYSQL_CONFIG
from utils import print_header

def connect_mysql():
    """
    Kết nối MySQL
    """
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        print("✓ Kết nối MySQL thành công!")
        return connection
    except Error as e:
        print(f"✗ Lỗi kết nối MySQL: {e}")
        return None

def load_eta_results(cursor, eta_report, ship_df):
    """
    Load kết quả ETA vào MySQL (bao gồm latitude và longitude của tàu)
    """
    print("\n📊 Đang load ETA results...")
    
    # Tạo bản sao và đổi tên cột
    eta_data = eta_report.copy()
    eta_data.columns = ['ship_name', 'port_from', 'port_to', 'eta_expected', 
                       'delay_hours', 'status', 'reason', 'distance_to_hazard']
    
    # Lấy thông tin kinh độ vĩ độ từ ship_df
    ship_coords = ship_df[['ship_name', 'latitude_ship', 'longitude_ship']].copy()
    ship_coords.columns = ['ship_name', 'latitude', 'longitude']
    
    # Merge để có đầy đủ thông tin
    eta_data = eta_data.merge(ship_coords, on='ship_name', how='left')
    
    # Sắp xếp lại thứ tự cột: ship_name, port_from, port_to, latitude, longitude, eta_expected, ...
    eta_data = eta_data[['ship_name', 'port_from', 'port_to', 'latitude', 'longitude',
                         'eta_expected', 'delay_hours', 'status', 'reason', 'distance_to_hazard']]
    
    if eta_data['eta_expected'].dtype == 'object':
        eta_data['eta_expected'] = pd.to_datetime(eta_data['eta_expected'])
    
    eta_data = eta_data.replace({np.nan: None})
    
    insert_eta = """
    INSERT INTO eta_results 
    (ship_name, port_from, port_to, latitude, longitude, eta_expected, delay_hours, status, reason, distance_to_hazard)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    eta_records = [tuple(row) for row in eta_data.values]
    cursor.executemany(insert_eta, eta_records)
    
    print(f"  ✓ Đã load {len(eta_records)} tàu vào eta_results")
    return len(eta_records)

def load_storm_info(cursor, storm_df):
    """
    Load thông tin bão vào MySQL
    """
    print("\n🌪️ Đang load storm info...")
    
    storm_data = storm_df.replace({np.nan: None})
    
    insert_storm = """
    INSERT INTO storm_info 
    (storm_id, name, latitude, longitude, wind_kmh, level, radius_km, warning_radius_km)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    storm_records = [tuple(row) for row in storm_data.values]
    cursor.executemany(insert_storm, storm_records)
    
    print(f"  ✓ Đã load {len(storm_records)} bão vào storm_info")
    return len(storm_records)

def load_weather_data(cursor, df_weather, sample_size=1000):
    """
    Load dữ liệu thời tiết vào MySQL
    """
    print("\n🌤️ Đang load weather data...")
    
    weather_sample = df_weather.sample(n=min(sample_size, len(df_weather)), random_state=42)
    
    weather_cols = ['Temperature', 'Humidity', 'Wind_Speed_kmh', 'Cloud_Cover',
                   'Pressure', 'significant_wave_height', 'mean_wave_period',
                   'latitude', 'longitude', 'is_rain_zone', 'storm_cluster']
    
    weather_data = weather_sample[weather_cols].replace({np.nan: None})
    
    insert_weather = """
    INSERT INTO weather_combined 
    (temperature, humidity, wind_speed_kmh, cloud_cover, pressure, 
     significant_wave_height, mean_wave_period, latitude, longitude, 
     is_rain_zone, storm_cluster)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    weather_records = [tuple(row) for row in weather_data.values]
    cursor.executemany(insert_weather, weather_records)
    
    print(f"  ✓ Đã load {len(weather_records)} dòng vào weather_combined")
    return len(weather_records)

def load_port_data(cursor, df_ports):
    """
    Load dữ liệu cảng biển vào MySQL
    """
    print("\n⚓ Đang load danh sách cảng biển...")
    
    if df_ports is None:
        print("  ! Không có dữ liệu cảng để load")
        return 0
    
    df_ports = df_ports.replace({np.nan: None})
    
    insert_ports = """
    INSERT INTO sea_ports 
    (region, port_name, country, latitude, longitude, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    port_records = [tuple(row) for row in df_ports.values]
    cursor.executemany(insert_ports, port_records)
    
    print(f"  ✓ Đã load {len(port_records)} cảng vào sea_ports")
    return len(port_records)

def print_statistics(cursor):
    """
    In thống kê sau khi load
    """
    print_header("✅ LOAD HOÀN TẤT!")
    
    cursor.execute("SELECT status, COUNT(*) FROM eta_results GROUP BY status")
    print("\n📈 Phân bố trạng thái:")
    for status, count in cursor.fetchall():
        print(f"  • {status}: {count} tàu")
    
    cursor.execute("SELECT COUNT(*) FROM storm_info")
    print(f"\n🌪️ Tổng số bão: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM weather_combined")
    print(f"🌤️ Tổng số mẫu thời tiết: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM sea_ports")
    print(f"⚓ Tổng số cảng đã load: {cursor.fetchone()[0]}")

def load_all_to_mysql(eta_report, storm_df, df_weather, df_ports, ship_df):
    """
    Load tất cả dữ liệu vào MySQL
    """
    print_header("📤 BẮT ĐẦU LOAD KẾT QUẢ VÀO MYSQL")
    
    connection = connect_mysql()
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Load từng loại dữ liệu (truyền thêm ship_df cho eta_results)
        load_eta_results(cursor, eta_report, ship_df)
        load_storm_info(cursor, storm_df)
        load_weather_data(cursor, df_weather)
        load_port_data(cursor, df_ports)
        
        # Commit
        connection.commit()
        
        # Thống kê
        print_statistics(cursor)
        
        print_header("💾 DỮ LIỆU ĐÃ SẴN SÀNG TRONG MYSQL!")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"\n✗ Lỗi MySQL: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Lỗi không xác định: {e}")
        return False