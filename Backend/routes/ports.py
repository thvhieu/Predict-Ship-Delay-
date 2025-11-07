from fastapi import APIRouter, HTTPException
from db.database import get_db_connection
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/api/ports")
async def get_ports():
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                id,
                port_name as name,
                region,
                country,
                latitude,
                longitude,
                status
            FROM sea_ports
            ORDER BY port_name
        """
        
        cursor.execute(query)
        ports = cursor.fetchall()
        
        # Process and format the results
        formatted_ports = []
        for port in ports:
            try:
                def convert_coordinate(coord, is_longitude=False):
                    if coord is None:
                        return None
                    try:
                        # Convert to float directly since coordinates are already in decimal degrees
                        coord_float = float(coord)
                        
                        # Validate range
                        if is_longitude and abs(coord_float) > 180:
                            logger.warning(f"Invalid longitude value: {coord_float}")
                            return None
                        if not is_longitude and abs(coord_float) > 90:
                            logger.warning(f"Invalid latitude value: {coord_float}")
                            return None
                            
                        return round(coord_float, 6)  # Round to 6 decimal places
                        
                    except Exception as e:
                        logger.error(f"Error converting coordinate {coord}: {str(e)}")
                        return None

                formatted_port = {
                    "id": port["id"],
                    "name": port["name"],
                    "region": port["region"],
                    "country": port["country"],
                    "location": {
                        "latitude": convert_coordinate(port["latitude"], False),
                        "longitude": convert_coordinate(port["longitude"], True)
                    },
                    "status": port["status"] or "ổn định",
                    "dockedShips": 0,  # Temporary default value
                    "capacity": 100,    # Temporary default value
                    "availableSlots": 100,  # Temporary default value
                    "avgWaitingTime": "N/A"  # Temporary default value
                }
                formatted_ports.append(formatted_port)
            except Exception as e:
                logger.error(f"Error processing port {port['id']}: {str(e)}")
                continue
        
        return {"ports": formatted_ports}
        
    except Exception as e:
        logger.error(f"Error fetching ports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@router.get("/api/ports/{port_id}")
async def get_port(port_id: int):
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection error")
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                id,
                port_name as name,
                region,
                country,
                latitude,
                longitude,
                status,
                created_at
            FROM sea_ports
            WHERE id = %s
        """
        
        cursor.execute(query, (port_id,))
        port = cursor.fetchone()
        
        if not port:
            raise HTTPException(status_code=404, detail="Port not found")
        
        return {
            "id": port["id"],
            "name": port["name"],
            "region": port["region"],
            "country": port["country"],
            "location": {
                "latitude": float(port["latitude"]) if port["latitude"] else None,
                "longitude": float(port["longitude"]) if port["longitude"] else None
            },
            "status": port["status"] or "ổn định",
            "last_updated": port["created_at"].isoformat() if port["created_at"] else None
        }
        
    except Exception as e:
        logger.error(f"Error fetching port {port_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()