"""
HỆ THỐNG DỰ ĐOÁN ETA - MƯA TRƯỚC, BÃO SAU
File chính điều phối toàn bộ hệ thống

Chạy: python main.py
"""

from utils import print_header
from data_loader import (
    load_weather_data, 
    augment_storm_data, 
    load_ship_data,
    load_port_data
)
from rain_model import detect_rain_zones, predict_rain_impact
from storm_model import detect_storm_centers, predict_storm_impact
from report_generator import generate_eta_report, save_reports, print_summary
from db_loader import load_all_to_mysql

def main():
    """
    Hàm chính - chạy toàn bộ pipeline
    """
    print_header("HỆ THỐNG DỰ ĐOÁN ETA - MƯA TRƯỚC, BÃO SAU")
    
    # ===== BƯỚC 1: LOAD DỮ LIỆU =====
    print_header("📁 BƯỚC 1: LOAD DỮ LIỆU")
    
    df_weather = load_weather_data()
    df_weather = augment_storm_data(df_weather)
    ship_df = load_ship_data()
    df_ports = load_port_data()
    
    # ===== BƯỚC 2: MODEL MƯA (CHẠY TRƯỚC) =====
    print_header("🌧️ BƯỚC 2: DỰ ĐOÁN ẢNH HƯỞNG MƯA")
    
    rain_zones = detect_rain_zones(df_weather)
    ship_df = predict_rain_impact(ship_df, rain_zones)
    
    # ===== BƯỚC 3: MODEL BÃO (CHẠY SAU, OVERRIDE) =====
    print_header("🌪️ BƯỚC 3: DỰ ĐOÁN ẢNH HƯỞNG BÃO")
    
    storm_df, df_weather = detect_storm_centers(df_weather)
    ship_df = predict_storm_impact(ship_df, storm_df)
    
    # ===== BƯỚC 4: TẠO BÁO CÁO =====
    print_header("📊 BƯỚC 4: TẠO BÁO CÁO")
    
    eta_report = generate_eta_report(ship_df)
    save_reports(eta_report, storm_df, df_weather)
    print_summary(ship_df, eta_report)
    
    # ===== BƯỚC 5: LOAD VÀO MYSQL (TRUYỀN THÊM ship_df) =====
    print_header("💾 BƯỚC 5: LOAD DỮ LIỆU VÀO MYSQL")
    
    success = load_all_to_mysql(eta_report, storm_df, df_weather, df_ports, ship_df)
    
    if success:
        print_header("✅ HỆ THỐNG HOÀN TẤT THÀNH CÔNG!")
        print("\n📁 Các file đã tạo:")
        print("  • ship_eta_report.csv")
        print("  • storm_info.csv")
        print("  • weather_combined.csv")
        print("\n💾 Dữ liệu đã load vào MySQL database: shipping_ml")
    else:
        print_header("⚠️ HỆ THỐNG HOÀN TẤT NHƯNG CÓ LỖI KHI LOAD VÀO MYSQL")
        print("Vui lòng kiểm tra:")
        print("  • MySQL server đã chạy?")
        print("  • Database 'shipping_ml' đã tạo?")
        print("  • Thông tin kết nối trong config.py đúng?")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Người dùng dừng chương trình")
    except Exception as e:
        print(f"\n\n✗ Lỗi không xác định: {e}")
        import traceback
        traceback.print_exc()