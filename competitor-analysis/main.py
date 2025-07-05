from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from services.places_service import PlacesService
from services.tavily_service import TavilyService
from services.analysis_service import AnalysisService
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

# Initialize services
tavily_service = TavilyService(api_key=os.getenv("TAVILY_API_KEY")) if os.getenv("TAVILY_API_KEY") else None
analysis_service = AnalysisService(openai_api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
places_service = PlacesService(
    api_key=os.getenv("GOOGLE_PLACES_API_KEY"),
    tavily_service=tavily_service,
    analysis_service=analysis_service
)

@app.post("/api/v1/competitors/analyze", response_model=CompetitorAnalysisResponse)
async def analyze_competitors(request: CompetitorAnalysisRequest):
    try:
        analysis = await places_service.analyze_competitors(request)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CompetitorCountRequest(BaseModel):
    business_type: str
    location: str
    max_results: int = 20
    min_rating: float = 0.0

class CompetitorCountResponse(BaseModel):
    competitor_count: int
    business_type: str
    location: str
    search_query: str

@app.post("/api/v1/competitors/count", response_model=CompetitorCountResponse)
async def count_competitors(request: CompetitorCountRequest):
    """
    Simple endpoint to count competitors in an area without full analysis.
    Returns just the number of competitors found.
    """
    try:
        search_query = f"{request.business_type} in {request.location}"
        
        # Use the places service to search but only get the count
        places_data = await places_service._search_places(
            query=search_query,
            max_results=request.max_results,
            min_rating=request.min_rating,
            open_now=False
        )
        
        competitor_count = len(places_data)
        
        return CompetitorCountResponse(
            competitor_count=competitor_count,
            business_type=request.business_type,
            location=request.location,
            search_query=search_query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)