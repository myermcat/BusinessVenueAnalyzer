"""
business_proximity_api.py
A simple wrapper around the Google Places API for querying nearby businesses by type.

Usage Example:
    >>> from metrics.traffic.traffic_school_business_proximity.business_proximity_api import BusinessProximityAPI
    >>> api = BusinessProximityAPI(api_key="YOUR_GOOGLE_API_KEY")
    >>> results = api.search_by_type("school", "Centretown Ottawa", max_results=10)
    >>> for place in results:
    ...     print(place["name"], place["address"])

Dependencies:
    - httpx for async HTTP requests
    - dotenv for environment variable management

The wrapper exposes helpers for searching businesses by type and location,
following the same pattern as the parking_api module.
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _log_request(query: str, max_results: int, min_rating: float) -> None:
    """Internal helper to log outgoing requests."""
    logger.debug(
        "Requesting places search: query=%s, max_results=%d, min_rating=%.1f",
        query, max_results, min_rating
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
class BusinessProximityAPI:
    """Wrapper around Google Places API for business proximity searches."""

    DEFAULT_MAX_RESULTS = 10
    DEFAULT_MIN_RATING = 0.0

    def __init__(self, api_key: str, *, timeout: int = 15) -> None:
        if not api_key:
            raise ValueError("`api_key` must be provided and non-empty.")

        self._api_key = api_key
        self._timeout = timeout
        logger.debug("Initialized BusinessProximityAPI with timeout=%ss", timeout)

    # -------------------------------------------------------------------
    # Core helper (text search)
    # -------------------------------------------------------------------
    async def search_by_type(
        self,
        place_type: str,
        location: str,
        *,
        max_results: int | None = None,
        min_rating: float | None = None,
    ) -> List[Dict[str, Any]]:
        """Search for places of a specific type near a location.

        Args:
            place_type: Type of place to search for (e.g., "school", "restaurant").
            location: Location description (e.g., "Centretown Ottawa").
            max_results: Maximum number of results to return (default: 10).
            min_rating: Minimum rating threshold (default: 0.0).

        Returns:
            List of place dictionaries with standardized fields.
        """
        if max_results is None:
            max_results = self.DEFAULT_MAX_RESULTS
        if min_rating is None:
            min_rating = self.DEFAULT_MIN_RATING

        text_query = f"{place_type} in {location}"
        _log_request(text_query, max_results, min_rating)

        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.id",
        }
        payload = {
            "textQuery": text_query,
            "pageSize": min(max_results, 20),
            "minRating": min_rating,
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, json=payload, timeout=self._timeout)
                resp.raise_for_status()
                places_data = resp.json().get("places", [])
            except Exception as e:
                logger.error("Google Places API error: %s", e)
                raise

        return [self._normalize_place(place) for place in places_data]

    async def search_multiple_types(
        self,
        place_types: List[str],
        location: str,
        *,
        max_results: int | None = None,
        min_rating: float | None = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search for multiple place types near a location.

        Args:
            place_types: List of place types to search for.
            location: Location description.
            max_results: Maximum number of results per type.
            min_rating: Minimum rating threshold.

        Returns:
            Dictionary mapping place types to lists of places.
        """
        results = {}
        for place_type in place_types:
            results[place_type] = await self.search_by_type(
                place_type, location, max_results=max_results, min_rating=min_rating
            )
        return results

    # -------------------------------------------------------------------
    # Utility helpers
    # -------------------------------------------------------------------
    def _normalize_place(self, place: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a place result to standard format."""
        return {
            "place_id": place.get("id", ""),
            "name": place.get("displayName", {}).get("text", "Unknown"),
            "address": place.get("formattedAddress", ""),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("userRatingCount"),
            "price_level": self._parse_price_level(place.get("priceLevel")),
        }

    @staticmethod
    def _parse_price_level(price_level: str | None) -> str:
        """Parse Google's price level enum to readable format."""
        if not price_level:
            return "Unknown"
        
        mapping = {
            "PRICE_LEVEL_FREE": "Free",
            "PRICE_LEVEL_INEXPENSIVE": "$",
            "PRICE_LEVEL_MODERATE": "$$",
            "PRICE_LEVEL_EXPENSIVE": "$$$",
            "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
        }
        return mapping.get(price_level, "Unknown")

    @staticmethod
    def summarize(place: Dict[str, Any]) -> Dict[str, Any]:
        """Return concise subset of a place result."""
        return {
            "place_id": place.get("place_id"),
            "name": place.get("name"),
            "address": place.get("address"),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
        }


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------
_api_instance: BusinessProximityAPI | None = None

def _get_api() -> BusinessProximityAPI:
    """Get or create singleton API instance."""
    global _api_instance
    if _api_instance is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set in environment")
        _api_instance = BusinessProximityAPI(api_key=api_key)
    return _api_instance


async def fetch_business_proximity(
    *,
    place_types: str,
    location: str,
    max_results: int = 10,
    min_rating: float = 0.0,
) -> Dict[str, List[Dict[str, Any]]]:
    """Async helper for fetching business proximity data.

    Args:
        place_types: Comma-separated place types (e.g., "school,library").
        location: Location description.
        max_results: Maximum results per type.
        min_rating: Minimum rating threshold.

    Returns:
        Dictionary mapping place types to lists of places.
    """
    api = _get_api()
    types_list = [t.strip() for t in place_types.split(",") if t.strip()]
    return await api.search_multiple_types(types_list, location, max_results=max_results, min_rating=min_rating)


def get_business_proximity(
    *,
    place_types: str,
    location: str,
    max_results: int = 10,
    min_rating: float = 0.0,
    loop: asyncio.AbstractEventLoop | None = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Sync wrapper around fetch_business_proximity for ease of use.

    If no running event-loop is detected, one is created temporarily.
    """
    coro = fetch_business_proximity(
        place_types=place_types,
        location=location,
        max_results=max_results,
        min_rating=min_rating,
    )
    try:
        loop = loop or asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop).result()
    else:
        return asyncio.run(coro)


# ---------------------------------------------------------------------------
# CLI usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Query business places via Google Places API")
    parser.add_argument("place_types", help="Comma-separated place types (e.g., 'school,library')")
    parser.add_argument("location", help="Location description (e.g., 'Centretown Ottawa')")
    parser.add_argument("--max-results", type=int, default=BusinessProximityAPI.DEFAULT_MAX_RESULTS)
    parser.add_argument("--min-rating", type=float, default=BusinessProximityAPI.DEFAULT_MIN_RATING)
    parser.add_argument(
        "--api-key", dest="api_key", default=os.getenv("GOOGLE_API_KEY"), help="Google API key"
    )
    args = parser.parse_args()

    if not args.api_key:
        parser.error("Google API key required via --api-key or GOOGLE_API_KEY env var")

    results = get_business_proximity(
        place_types=args.place_types,
        location=args.location,
        max_results=args.max_results,
        min_rating=args.min_rating,
    )
    
    summaries = {}
    for place_type, places in results.items():
        summaries[place_type] = [BusinessProximityAPI.summarize(p) for p in places]
    
    print(json.dumps(summaries, indent=2))
