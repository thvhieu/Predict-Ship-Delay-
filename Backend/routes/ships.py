from fastapi import APIRouter, HTTPException
from datetime import datetime
try:
    from ..db.database import get_db_connection
except Exception:
    from db.database import get_db_connection

router = APIRouter()

@router.get("/api/ships")
async def get_ships():
    """Return ship list from eta_results table."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = conn.cursor(dictionary=True)

        # Lấy dữ liệu từ bảng eta_results và join với sea_ports để lấy tọa độ của cảng đích
        query = """
            SELECT 
                er.ship_name,
                er.port_from,
                er.port_to,
                er.eta_expected,
                er.delay_hours,
                er.status,
                er.reason,
                sp.latitude,
                sp.longitude
            FROM eta_results er
            LEFT JOIN sea_ports sp ON er.port_to = sp.port_name
            WHERE er.eta_expected > NOW()
            ORDER BY er.eta_expected ASC
        """
            
        cursor.execute(query)
        rows = cursor.fetchall()

        # Chuyển đổi dữ liệu theo định dạng frontend cần
        results = []
        for r in rows:
            ship_data = {
                'id': r['ship_name'],
                'name': r['ship_name'],
                'route': f"{r['port_from']} → {r['port_to']}",
                'eta': r['eta_expected'].isoformat() if isinstance(r['eta_expected'], datetime) else r['eta_expected'],
                'delay_hours': float(r['delay_hours']) if r['delay_hours'] is not None else 0,
                'status': r['status'] or 'active',
                'reason': r['reason'],
                'lat': float(r['latitude']) if r['latitude'] is not None else None,
                'lng': float(r['longitude']) if r['longitude'] is not None else None
            }
            results.append(ship_data)

        cursor.close()
        conn.close()
        return results

    except Exception as e:
        # ensure connection closed on error
        if 'cursor' in locals():
            try:
                cursor.close()
            except:
                pass
        if 'conn' in locals():
            try:
                conn.close()
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
