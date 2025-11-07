from fastapi import APIRouter, HTTPException
from db.database import get_db_connection
from typing import List
from pydantic import BaseModel
from datetime import datetime
import pytz

router = APIRouter()

class StormAlert(BaseModel):
    alert_id: int
    message: str
    severity: str
    status: str
    latitude: float
    longitude: float
    radius_km: float
    warning_radius_km: float
    wind_kmh: float

class StormInfo(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    wind_kmh: float
    level: str
    radius_km: float
    warning_radius_km: float

@router.get("/api/storms", response_model=List[StormInfo])
async def get_storms():
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, name, latitude, longitude, 
                   wind_kmh, level, radius_km, warning_radius_km
            FROM storm_info
            ORDER BY wind_kmh DESC
        """
        cursor.execute(query)
        storms = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return storms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/storm-alerts", response_model=List[StormAlert])
async def get_storm_alerts():
    try:
        print("Starting to fetch storm alerts...")
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        cursor = conn.cursor(dictionary=True)
        print("Database connection successful")
        query = """
            SELECT 
                id as alert_id,
                name as message,
                latitude,
                longitude,
                radius_km,
                warning_radius_km,
                wind_kmh,
                CASE
                    WHEN level = 'Super Typhoon' THEN 'critical'
                    WHEN level IN ('Category 5', 'Category 4') THEN 'high'
                    WHEN level IN ('Category 3', 'Category 2', 'Category 1') THEN 'medium'
                    ELSE 'low'
                END as severity,
                CASE
                    WHEN wind_kmh > 150 THEN 'Siêu bão'
                    WHEN wind_kmh > 120 THEN 'Bão mạnh'
                    WHEN wind_kmh > 80 THEN 'Bão'
                    ELSE 'Áp thấp nhiệt đới'
                END as status
            FROM storm_info
            ORDER BY 
                CASE level
                    WHEN 'Super Typhoon' THEN 1
                    WHEN 'Category 5' THEN 2
                    WHEN 'Category 4' THEN 3
                    WHEN 'Category 3' THEN 4
                    WHEN 'Category 2' THEN 5
                    WHEN 'Category 1' THEN 6
                    WHEN 'Tropical Storm' THEN 7
                    ELSE 8
                END,
                wind_kmh DESC
        """
        print("Executing query:", query)
        cursor.execute(query)
        alerts = cursor.fetchall()
        
        print(f"Found {len(alerts)} alerts")
        
        cursor.close()
        conn.close()
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))