from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from services.places_service import PlacesService
from models.competitor_models import CompetitorAnalysisRequest, CompetitorAnalysisResponse

load_dotenv()

app = FastAPI(title="Business Competitor Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

places_service = PlacesService(api_key=os.getenv("GOOGLE_PLACES_API_KEY"))

@app.post("/api/v1/competitors/analyze", response_model=CompetitorAnalysisResponse)
async def analyze_competitors(request: CompetitorAnalysisRequest):
    try:
        analysis = await places_service.analyze_competitors(request)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)