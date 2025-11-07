"""
Module tạo báo cáo kết quả
"""
import pandas as pd
from config import OUTPUT_PATHS
from utils import format_report, print_header

def generate_eta_report(ship_df):
    """
    Tạo báo cáo ETA
    """
    eta_report = ship_df[[
        'ship_name', 
        'port_from',
        'port_to',
        'ETA',
        'delay_hours',
        'status',
        'reason',
        'distance_to_hazard'
    ]].copy()
    
    eta_report.columns = [
        'Tên tàu',
        'Từ',
        'Đến', 
        'ETA (Dự kiến)',
        'Delay (giờ)',
        'Status',
        'Nguyên nhân',
        'Khoảng cách (km)'
    ]
    
    # Format và sắp xếp
    eta_report = format_report(eta_report)
    eta_report['ETA (Dự kiến)'] = eta_report['ETA (Dự kiến)'].dt.strftime('%Y-%m-%d %H:%M')
    
    return eta_report

def save_reports(eta_report, storm_df, df_weather):
    """
    Lưu các file báo cáo
    """
    print_header("💾 ĐANG LƯU BÁO CÁO")
    
    try:
        eta_report.to_csv(OUTPUT_PATHS['eta_report'], index=False, encoding='utf-8-sig')
        print(f"✓ Đã lưu {OUTPUT_PATHS['eta_report']}")
        
        storm_df.to_csv(OUTPUT_PATHS['storm_info'], index=False)
        print(f"✓ Đã lưu {OUTPUT_PATHS['storm_info']}")
        
        df_weather.to_csv(OUTPUT_PATHS['weather_combined'], index=False)
        print(f"✓ Đã lưu {OUTPUT_PATHS['weather_combined']}")
        
        return True
    except Exception as e:
        print(f"✗ Lỗi khi lưu file: {e}")
        return False

def print_summary(ship_df, eta_report):
    """
    In tóm tắt kết quả
    """
    print_header("BẢNG DỰ ĐOÁN ETA CUỐI CÙNG (TOP 50)")
    print(eta_report.head(50).to_string(index=False, max_colwidth=25))
    
    print_header("THỐNG KÊ CHI TIẾT")
    
    n_delay = len(ship_df[ship_df['status'] == 'Trễ'])
    n_risk = len(ship_df[ship_df['status'] == 'Nguy cơ'])
    n_ontime = len(ship_df[ship_df['status'] == 'Đúng giờ'])
    
    n_risk_rain = len(ship_df[(ship_df['status'] == 'Nguy cơ') & 
                              (ship_df['reason'].str.contains('Vùng mưa', na=False))])
    n_risk_storm = len(ship_df[(ship_df['status'] == 'Nguy cơ') & 
                               (ship_df['reason'].str.contains('Gần bão', na=False))])
    
    avg_delay = ship_df[ship_df['delay_hours'] > 0]['delay_hours'].mean() if n_delay + n_risk > 0 else 0
    
    print(f"\n📊 Tổng quan:")
    print(f"  • Tổng số tàu: {len(ship_df)}")
    print(f"  • Trễ: {n_delay} tàu ({n_delay/len(ship_df)*100:.1f}%)")
    print(f"  • Nguy cơ: {n_risk} tàu ({n_risk/len(ship_df)*100:.1f}%)")
    print(f"    - Do mưa: {n_risk_rain}")
    print(f"    - Do bão: {n_risk_storm}")
    print(f"  • Đúng giờ: {n_ontime} tàu ({n_ontime/len(ship_df)*100:.1f}%)")
    print(f"\n⏱️ Thời gian trễ trung bình: {avg_delay:.2f} giờ")