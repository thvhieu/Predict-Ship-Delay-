"""
Các hàm tiện ích dùng chung
"""
from math import radians, cos, sin, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa 2 điểm trên Trái Đất (km)
    """
    R = 6371  # Bán kính Trái Đất (km)
    
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

def classify_storm_level(wind_speed):
    """
    Phân loại cấp độ bão theo tốc độ gió
    """
    if wind_speed > 155:
        return "Siêu bão"
    elif wind_speed > 130:
        return "Bão mạnh"
    elif wind_speed > 100:
        return "Bão"
    else:
        return "Áp thấp nhiệt đới"

def format_report(df):
    """
    Format dataframe cho báo cáo
    """
    df = df.copy()
    
    # Sắp xếp theo độ ưu tiên
    status_order = {'Trễ': 0, 'Nguy cơ': 1, 'Đúng giờ': 2}
    df['sort_key'] = df['Status'].map(status_order)
    df = df.sort_values(['sort_key', 'Delay (giờ)'], ascending=[True, False])
    df = df.drop('sort_key', axis=1)
    
    return df

def print_header(title):
    """
    In header đẹp
    """
    print("\n" + "="*70)
    print(title)
    print("="*70)