# Census Demographics API

A FastAPI service that provides demographic analysis using Canadian census data.

## Features

- Population density analysis
- Median income calculations
- Dwelling value statistics  
- Age demographics
- Household size analysis
- Walking and driving radius support

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8001`

## API Endpoints

### POST /api/v1/census/analyze
Analyze demographics for a location within specified radii.

**Request Body:**
```json
{
  "latitude": 45.4215,
  "longitude": -75.6972,
  "walking_radius_km": 1.0,
  "driving_radius_km": 5.0,
  "include_detailed_areas": false
}
```

**Response:** Comprehensive demographic statistics for both walking and driving radii.

### GET /api/v1/census/health
Health check endpoint.

### GET /api/v1/census/stats
Get statistics about the loaded census data.

## Example Usage

### Using Text Address (Recommended)
```bash
curl -X POST "http://localhost:8001/api/v1/census/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "centretown ottawa canada",
    "walking_radius_km": 1.0,
    "driving_radius_km": 5.0
  }'
```

### Using Coordinates
```bash
curl -X POST "http://localhost:8001/api/v1/census/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 45.4215,
    "longitude": -75.6972,
    "walking_radius_km": 1.0,
    "driving_radius_km": 5.0
  }'
```