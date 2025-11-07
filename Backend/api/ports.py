from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'shipping_ml')
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.get("/api/ports/{port_id}")
async def get_port_info(port_id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT port_name, region, country, latitude, longitude, status, created_at
            FROM sea_ports
            WHERE id = %s
        """, (port_id,))
        
        port_info = cursor.fetchone()
        if not port_info:
            raise HTTPException(status_code=404, detail="Port not found")
        
        response = {
            "portName": port_info['port_name'],
            "region": port_info['region'],
            "country": port_info['country'],
            "status": port_info['status'],
            "location": {
                "latitude": port_info['latitude'],
                "longitude": port_info['longitude']
            },
            "lastUpdated": port_info['created_at'].isoformat()
        }
        
        return response
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get("/api/ports")
async def get_ports_list():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, port_name, region, country, latitude, longitude, status
            FROM sea_ports
        """)
        ports = cursor.fetchall()
        
        return {
            "ports": [
                {
                    "id": port['id'],
                    "name": port['port_name'],
                    "region": port['region'],
                    "country": port['country'],
                    "status": port['status'],
                    "location": {
                        "latitude": port['latitude'],
                        "longitude": port['longitude']
                    }
                }
                for port in ports
            ]
        }
        
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()