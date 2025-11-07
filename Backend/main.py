from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import ports, eta, ships, storm

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(ports.router)
app.include_router(eta.router)
app.include_router(ships.router)
app.include_router(storm.router)

@app.get("/")
async def root():
    return {"message": "Shipping ML API is running"}