"""Simple helper that wraps the Business Proximity micro-service for use inside
internal metric computations.

The wrapper keeps a singleton `ProximityService` instance initialised with the
`GOOGLE_PLACES_API_KEY` from the environment and exposes both asynchronous and
synchronous call helpers.

Example
-------
>>> from metrics.traffic.traffic_school_business_proximity.business_proximity_api import get_business_proximity
>>> response = get_business_proximity(
...     place_types="school,library",
...     location="Centretown Ottawa",
...     radius_meters=1500,
... )
>>> print(response.results["school"])
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

from dotenv import load_dotenv

# Import the service & models from the previously created business_proximity package.
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_PLACES_API_KEY not set in environment or .env file")

app = FastAPI(title="Business Proximity API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class BusinessProximityRequest(BaseModel):
    places_type: str = Field(..., description="Comma-separated Google place types, e.g. 'cafe,restaurant'")
    location: str = Field(..., description="Location description, e.g. 'Centretown Ottawa'")
    max_results: int = Field(10, ge=1, le=20)
    min_rating: float = Field(0.0, ge=0.0, le=5.0)
    enable_deep_analysis: bool = False

class Place(BaseModel):
    name: str
    address: str
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[str] = None
    place_id: str

class QueryInfo(BaseModel):
    location: str
    place_types: List[str]
    timestamp: datetime
    max_results: int
    min_rating: float

class DeepAnalysis(BaseModel):
    average_rating: Optional[float] = None
    total_places: int = 0

class BusinessProximityResponse(BaseModel):
    query_info: QueryInfo
    results: Dict[str, List[Place]]
    deep_analysis: Optional[DeepAnalysis] = None

def parse_price_level(price_level: str) -> str:
    mapping = {
        "PRICE_LEVEL_FREE": "Free",
        "PRICE_LEVEL_INEXPENSIVE": "$",
        "PRICE_LEVEL_MODERATE": "$$",
        "PRICE_LEVEL_EXPENSIVE": "$$$",
        "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
    }
    return mapping.get(price_level, "Unknown")

async def search_places(text_query: str, max_results: int, min_rating: float) -> List[dict]:
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.id",
    }
    payload = {
        "textQuery": text_query,
        "pageSize": min(max_results, 20),
        "minRating": min_rating,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json().get("places", [])

@app.post("/api/v1/business-proximity/analyze", response_model=BusinessProximityResponse)
async def analyze_business_proximity(body: BusinessProximityRequest):
    place_types = [p.strip() for p in body.places_type.split(",") if p.strip()]
    all_results: Dict[str, List[Place]] = {}
    all_ratings: List[float] = []
    for place_type in place_types:
        text_query = f"{place_type} in {body.location}"
        try:
            places_data = await search_places(text_query, body.max_results, body.min_rating)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Google Places API error: {e}")
        places = [
            Place(
                name=p.get("displayName", {}).get("text", "Unknown"),
                address=p.get("formattedAddress", ""),
                rating=p.get("rating"),
                user_ratings_total=p.get("userRatingCount"),
                price_level=parse_price_level(p.get("priceLevel")),
                place_id=p.get("id", ""),
            ) for p in places_data
        ]
        all_results[place_type] = places
        all_ratings.extend([pl.rating for pl in places if pl.rating is not None])
    query_info = QueryInfo(
        location=body.location,
        place_types=place_types,
        timestamp=datetime.now(),
        max_results=body.max_results,
        min_rating=body.min_rating,
    )
    deep_analysis = None
    if body.enable_deep_analysis:
        avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else None
        deep_analysis = DeepAnalysis(average_rating=avg_rating, total_places=len(all_ratings))
    return BusinessProximityResponse(
        query_info=query_info,
        results=all_results,
        deep_analysis=deep_analysis,
    )

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("metrics.traffic.traffic_school_business_proximity.business_proximity_api:app", host="0.0.0.0", port=8002, reload=True)

# Ensure .env variables are loaded when running outside of the FastAPI context
load_dotenv()

# Singleton service instance so we don't recreate an httpx client for every call
_service: ProximityService | None = None

def _get_service() -> ProximityService:
    global _service
    if _service is None:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_PLACES_API_KEY is not set in environment")
        _service = ProximityService(api_key=api_key)
    return _service


async def fetch_business_proximity(
    *,
    place_types: str,
    location: str,
    radius_meters: int = 2000,
    max_results: int = 10,
    min_rating: float = 0.0,
    open_now: bool = False,
) -> ProximitySearchResponse:
    """Async helper returning a `ProximitySearchResponse`.

    Parameters mirror the fields of `ProximitySearchRequest` for convenience.
    """
    request = ProximitySearchRequest(
        place_types=place_types,
        location=location,
        radius_meters=radius_meters,
        max_results=max_results,
        min_rating=min_rating,
        open_now=open_now,
    )

    service = _get_service()
    return await service.search(request)


def get_business_proximity(
    *,
    place_types: str,
    location: str,
    radius_meters: int = 2000,
    max_results: int = 10,
    min_rating: float = 0.0,
    open_now: bool = False,
    loop: asyncio.AbstractEventLoop | None = None,
) -> ProximitySearchResponse:
    """Sync wrapper around :pyfunc:`fetch_business_proximity` for ease of use.

    If no running event-loop is detected, one is created temporarily.
    """
    coro = fetch_business_proximity(
        place_types=place_types,
        location=location,
        radius_meters=radius_meters,
        max_results=max_results,
        min_rating=min_rating,
        open_now=open_now,
    )
    try:
        loop = loop or asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If we're already inside an asyncio context, schedule and wait.
        return asyncio.run_coroutine_threadsafe(coro, loop).result()
    else:
        return asyncio.run(coro)
