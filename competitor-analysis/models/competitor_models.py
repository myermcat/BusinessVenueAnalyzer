from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class CompetitorAnalysisRequest(BaseModel):
    business_type: str = Field(..., description="Type of business (e.g., 'cafe', 'restaurant')")
    location: str = Field(..., description="Location to search (e.g., 'centretown ottawa')")
    radius_meters: int = Field(default=1000, ge=100, le=50000, description="Search radius in meters")
    max_results: int = Field(default=10, ge=1, le=20, description="Maximum number of competitors to return")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Minimum rating filter")
    open_now: bool = Field(default=False, description="Filter for currently open businesses")
    enable_deep_analysis: bool = Field(default=True, description="Enable Phase 2 deep competitor analysis")

class OpeningHours(BaseModel):
    open_now: bool
    periods: Optional[List[Dict]] = None
    weekday_text: Optional[List[str]] = None

class Review(BaseModel):
    author_name: str
    rating: int
    text: str
    time: Optional[datetime] = None

class TavilySearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: float

class TavilyResponse(BaseModel):
    query: str
    ai_answer: Optional[str] = None
    results: List[TavilySearchResult] = []

class Competitor(BaseModel):
    name: str
    address: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_level: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    business_status: Optional[str] = None
    opening_hours: Optional[OpeningHours] = None
    top_reviews: List[Review] = []
    place_id: str
    competitor_analysis: Optional[str] = None
    data_sources: List[str] = []
    analysis_confidence: Optional[float] = None

class QueryInfo(BaseModel):
    business_type: str
    location: str
    search_query: str
    radius_meters: int
    timestamp: datetime
    total_results: int

class MarketInsights(BaseModel):
    average_rating: Optional[float] = None
    rating_distribution: Dict[str, int] = {}
    price_level_distribution: Dict[str, int] = {}
    total_reviews: int = 0
    highly_rated_count: int = 0
    market_saturation: str = "Unknown"

class CompetitorAnalysisResponse(BaseModel):
    query_info: QueryInfo
    competitors: List[Competitor]
    market_insights: MarketInsights