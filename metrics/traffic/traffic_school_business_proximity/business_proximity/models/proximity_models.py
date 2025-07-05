from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class ProximitySearchRequest(BaseModel):
    place_types: str = Field(..., description="Comma-separated Google place types (e.g., 'cafe,restaurant')")
    location: str = Field(..., description="Location for search (e.g., 'Centretown Ottawa')")
    radius_meters: int = Field(default=2000, ge=100, le=50000)
    max_results: int = Field(default=10, ge=1, le=20)
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    open_now: bool = Field(default=False)

class Place(BaseModel):
    name: str
    address: str
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[str] = None
    place_id: str

class QueryInfo(BaseModel):
    location: str
    radius_meters: int
    place_types: List[str]
    timestamp: datetime

class ProximitySearchResponse(BaseModel):
    query_info: QueryInfo
    results: Dict[str, List[Place]]