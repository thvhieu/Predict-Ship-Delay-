# Predict Ship Delay System

## Overview
A comprehensive system for predicting ship delays by analyzing weather conditions, tracking vessels, and calculating Estimated Time of Arrival (ETA). The system combines real-time weather data, historical shipping patterns, and machine learning models to provide accurate delay predictions.

## Key Features
- Real-time ship tracking and monitoring
- Weather condition analysis and storm tracking
- ETA calculation with machine learning
- Port information management
- Interactive map visualization

[![GitHub issues](https://img.shields.io/github/issues/thvhieu/Predict-Ship-Delay-)](https://github.com/thvhieu/Predict-Ship-Delay-/issues)
[![GitHub license](https://img.shields.io/github/license/thvhieu/Predict-Ship-Delay-)](https://github.com/thvhieu/Predict-Ship-Delay-/blob/main/LICENSE)

This project provides a system for tracking ships, monitoring weather conditions, and calculating ETA (Estimated Time of Arrival) for vessels.

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/thvhieu/Predict-Ship-Delay-.git
cd Predict-Ship-Delay-
```

## Quick Start with Docker

If you have Docker and Docker Compose installed, you can run the entire application with just one command:

```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost  or http://127.0.0.1
- Backend API: http://localhost:8000

To stop the application:
```bash
docker-compose down
```

## Manual Setup (Without Docker)

If you prefer to run the application without Docker, follow the instructions below.

## Project Structure

```
project_MIS/
├── Backend/           # FastAPI backend server
├── Frontend/          # Web interface
└── Machine_Learning/  # ML models and data processing
```

## Prerequisites

Before running this project, make sure you have:

1. Python 3.x installed
2. MySQL Server installed
3. Visual Studio Code (recommended) or any web server for static files
4. Web browser (Chrome/Firefox recommended)

## Setup Instructions

### 1. Database Setup

1. Open MySQL and login:
```sql
mysql -u root -p
```

2. Run the database setup script:
```sql
mysql -u root -p < test/reset_database.sql
```

### 2. Backend Setup

1. Navigate to Backend directory:
```powershell
cd Backend
```

2. Create a `.env` file with the following content:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=123456
DB_NAME=shipping_ml
```

3. Install required Python packages:
```powershell
pip install -r requirements.txt
```

4. Start the backend server:
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend server will be available at: http://localhost:8000

### 3. Frontend Setup

1. Open the Frontend folder in Visual Studio Code

2. Install "Live Server" or "Five Server" extension

3. Right-click on `index.html` and select "Open with Live Server"

The frontend will be available at: http://localhost:5500 (or similar port)

### 4. Machine Learning Setup

The Machine Learning component uses several data files:
- cang_bien_chau_a_14.csv
- danh_sach_tau_100.csv
- wave_clean1.csv
- weather_rain_clean1.csv
- weather_combined.csv
- weather_data_asia.csv

These files are included in the project and don't require additional setup.

## Features

- Real-time ship tracking
- Weather condition monitoring
- Storm tracking and warnings
- ETA calculation
- Port information management

## Troubleshooting

### Common Issues

1. Database Connection Failed
   - Check if MySQL is running
   - Verify credentials in `.env` file
   - Ensure database 'shipping_ml' exists

2. Backend Server Won't Start
   - Check if required ports are available (8000)
   - Verify all Python dependencies are installed
   - Check Python version compatibility

3. Frontend Not Loading
   - Ensure backend server is running
   - Check browser console for errors
   - Verify web server is serving the files correctly

## Additional Notes

- The backend runs on port 8000 by default
- Frontend requires an active internet connection for map features
- Make sure to keep the data files (.csv) in their respective directories
- Python 3.x is required (tested on Python 3.8+)

## Contact

For any questions or issues, please contact:
[Your Contact Information]