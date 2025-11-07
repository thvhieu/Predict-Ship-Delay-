from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error
from typing import Dict, Any
import os
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from routes import eta

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'shipping_ml')
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Port API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Port API Documentation</h1>
            <div class="endpoint">
                <h2>Get All Ports</h2>
                <p><strong>Endpoint:</strong> <code>GET /api/ports</code></p>
                <p>Returns a list of all ports in the system.</p>
                <p><a href="/api/ports">Try it</a></p>
            </div>
            <div class="endpoint">
                <h2>Get Port Details</h2>
                <p><strong>Endpoint:</strong> <code>GET /api/ports/{port_id}</code></p>
                <p>Returns detailed information about a specific port.</p>
                <p>Example: <a href="/api/ports/1">Get Port ID 1</a></p>
            </div>
            <div class="endpoint">
                <h2>API Documentation</h2>
                <p>For detailed API documentation:</p>
                <ul>
                    <li><a href="/docs">Swagger UI Documentation</a></li>
                    <li><a href="/redoc">ReDoc Documentation</a></li>
                </ul>
            </div>
        </body>
    </html>
    """

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


# Include routers
try:
    from routes import eta, storm
    app.include_router(eta.router)
    app.include_router(storm.router)
except Exception as e:
    print(f"Warning: could not include routers: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)