from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from db.database import get_db_connection
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, validator

router = APIRouter()

class ETAResponse(BaseModel):
    ship_name: str
    port_from: str
    port_to: str
    eta_expected: Optional[str] = None  # Changed to string to handle ISO format
    delay_hours: float
    status: str
    reason: Optional[str] = None
    distance_to_hazard: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    from_lat: Optional[float] = None
    from_lng: Optional[float] = None
    to_lat: Optional[float] = None
    to_lng: Optional[float] = None

    @validator('eta_expected', pre=True)
    def parse_datetime(cls, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    class Config:
        orm_mode = True

@router.get("/api/eta")
async def get_eta_info():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                e.ship_name,
                e.port_from,
                e.port_to,
                DATE_FORMAT(e.eta_expected, '%Y-%m-%dT%H:%i:%s') as eta_expected,
                COALESCE(CAST(e.delay_hours AS FLOAT), 0) as delay_hours,
                CASE 
                    WHEN COALESCE(e.delay_hours, 0) = 0 THEN 'active'
                    WHEN COALESCE(e.delay_hours, 0) > 4 THEN 'inactive'
                    ELSE 'warning'
                END as status,
                e.reason,
                COALESCE(CAST(e.distance_to_hazard AS FLOAT), 0) as distance_to_hazard,
                CAST(e.latitude AS DECIMAL(10,6)) as latitude,
                CAST(e.longitude AS DECIMAL(10,6)) as longitude,
                p1.latitude as from_lat,
                p1.longitude as from_lng,
                p2.latitude as to_lat,
                p2.longitude as to_lng
            FROM eta_results e
            LEFT JOIN sea_ports p1 ON e.port_from = p1.port_name
            LEFT JOIN sea_ports p2 ON e.port_to = p2.port_name
            WHERE e.latitude IS NOT NULL 
            AND e.longitude IS NOT NULL
            ORDER BY e.ship_name ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Process the results
        processed_results = []
        for row in results:
            # Convert None values to appropriate defaults
            row_dict = {
                "ship_name": row["ship_name"],
                "port_from": row["port_from"],
                "port_to": row["port_to"],
                "eta_expected": row["eta_expected"],
                "delay_hours": float(row["delay_hours"] or 0),
                "status": row["status"],
                "reason": row["reason"] or None,
                "distance_to_hazard": float(row["distance_to_hazard"] or 0),
                "latitude": float(row["latitude"]) if row["latitude"] is not None else None,
                "longitude": float(row["longitude"]) if row["longitude"] is not None else None
            }
            processed_results.append(row_dict)
            
        return JSONResponse(content=processed_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/eta/{ship_name}", response_model=ETAResponse)
async def get_ship_eta(ship_name: str):
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection error")
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                ship_name,
                port_from,
                port_to,
                eta_expected,
                CAST(delay_hours AS FLOAT) as delay_hours,
                CASE 
                    WHEN delay_hours = 0 THEN 'active'
                    WHEN delay_hours > 4 THEN 'inactive'
                    ELSE 'warning'
                END as status,
                reason,
                CAST(distance_to_hazard AS FLOAT) as distance_to_hazard,
                CAST(latitude AS FLOAT) as latitude,
                CAST(longitude AS FLOAT) as longitude
            FROM eta_results
            WHERE ship_name = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        cursor.execute(query, (ship_name,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))