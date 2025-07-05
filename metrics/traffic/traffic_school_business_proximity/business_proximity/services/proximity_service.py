import httpx
from typing import List, Dict
from datetime import datetime

from ..models.proximity_models import (
    ProximitySearchRequest,
    ProximitySearchResponse,
    Place,
    QueryInfo,
)

class ProximityService:
    """Async wrapper for Google Places API text search, supporting multiple place types."""

    SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, request: ProximitySearchRequest) -> ProximitySearchResponse:
        place_types = [p.strip() for p in request.place_types.split(",") if p.strip()]
        results: Dict[str, List[Place]] = {}

        for place_type in place_types:
            text_query = f"{place_type} in {request.location}"
            places_data = await self._search_places(
                text_query=text_query,
                max_results=request.max_results,
                min_rating=request.min_rating,
                open_now=request.open_now,
            )
            results[place_type] = [self._parse_place(p) for p in places_data]

        query_info = QueryInfo(
            location=request.location,
            radius_meters=request.radius_meters,
            place_types=place_types,
            timestamp=datetime.now(),
        )

        return ProximitySearchResponse(query_info=query_info, results=results)

    async def _search_places(
        self,
        *,
        text_query: str,
        max_results: int,
        min_rating: float,
        open_now: bool,
    ) -> List[Dict]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.id",
        }
        payload = {
            "textQuery": text_query,
            "pageSize": min(max_results, 20),
            "minRating": min_rating,
            "openNow": open_now,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.SEARCH_URL, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            return response.json().get("places", [])

    @staticmethod
    def _parse_place(place: Dict) -> Place:
        mapping = {
            "PRICE_LEVEL_FREE": "Free",
            "PRICE_LEVEL_INEXPENSIVE": "$",
            "PRICE_LEVEL_MODERATE": "$$",
            "PRICE_LEVEL_EXPENSIVE": "$$$",
            "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
        }
        return Place(
            name=place.get("displayName", {}).get("text", "Unknown"),
            address=place.get("formattedAddress", ""),
            rating=place.get("rating"),
            user_ratings_total=place.get("userRatingCount"),
            price_level=mapping.get(place.get("priceLevel"), "Unknown"),
            place_id=place.get("id", ""),
        )