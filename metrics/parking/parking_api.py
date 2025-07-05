"""
parking_api.py
A simple wrapper around the   Places (Maps) API for querying nearby parking lots.

Usage Example:
    >>> from metrics.parking.parking_api import ParkingAPI
    >>> api = ParkingAPI(api_key="YOUR_GOOGLE_API_KEY")
    >>> results = api.nearby(37.4221, -122.0841, radius=1000)
    >>> for place in results:
    ...     print(place["name"], place["vicinity"])

Dependencies:
    - googlemaps (https://github.com/googlemaps/google-maps-services-python)
      This dependency is already locked in `competitor-analysis/requirements.txt`.

The wrapper currently exposes a single helper (`nearby`) restricted to
`type="parking"`, aligning with the metrics requirement. Feel free to extend
this module with additional helpers (e.g. place details) as needed.
"""
from __future__ import annotations

import logging
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Tuple

try:
    import googlemaps  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The `googlemaps` package is required for `ParkingAPI`.\n"
        "Install it via `pip install googlemaps` and ensure you have a valid\n"
        "Google Maps/Places API key."
    ) from exc

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _log_request(location: Tuple[float, float], radius: int) -> None:
    """Internal helper to log outgoing requests."""
    logger.debug(
        "Requesting nearby parking: location=%s, radius=%dm", location, radius
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
class ParkingAPI:
    """Tiny wrapper around Google Places API restricted to *parking* type."""

    DEFAULT_RADIUS_METERS = 500  # Roughly 2–3 city blocks

    def __init__(self, api_key: str, *, timeout: int = 5) -> None:
        if not api_key:
            raise ValueError("`api_key` must be provided and non-empty.")

        self._client = googlemaps.Client(key=api_key, timeout=timeout)
        logger.debug("Initialized ParkingAPI client with timeout=%ss", timeout)

    # -------------------------------------------------------------------
    # Core helper (nearby search)
    # -------------------------------------------------------------------
    def nearby(
        self,
        latitude: float,
        longitude: float,
        *,
        radius: int | None = None,
        open_now: bool | None = None,
        language: str | None = None,
        page_token: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Return parking places near the specified coordinates.

        Args:
            latitude: Latitude of the search center.
            longitude: Longitude of the search center.
            radius: Search radius in meters (default: 500).
            open_now: Restrict to places currently open.
            language: Optional language code (e.g. "en").
            page_token: Paging token from previous response.
        """
        if radius is None:
            radius = self.DEFAULT_RADIUS_METERS

        location: Tuple[float, float] = (latitude, longitude)
        _log_request(location, radius)

        response: Dict[str, Any] = self._client.places_nearby(
            location=location,
            radius=radius,
            type="parking",
            open_now=open_now,
            language=language,
            page_token=page_token,
        )

        status = response.get("status")
        if status != "OK":
            logger.warning(
                "Google Places API returned non-OK status: %s | error_message=%s",
                status,
                response.get("error_message"),
            )

        return response.get("results", [])

    # Alias for clarity
    get_nearby_parking = nearby

    # -------------------------------------------------------------------
    # Utility helpers
    # -------------------------------------------------------------------
    @staticmethod
    def summarize(place: Dict[str, Any]) -> Dict[str, Any]:
        """Return concise subset of a place result."""
        return {
            "place_id": place.get("place_id"),
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "location": place.get("geometry", {}).get("location"),
        }


# ---------------------------------------------------------------------------
# CLI usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    import argparse, json, os

    parser = argparse.ArgumentParser(description="Query parking places via Google Places API")
    parser.add_argument("lat", type=float, help="Latitude of the search center")
    parser.add_argument("lng", type=float, help="Longitude of the search center")
    parser.add_argument("--radius", type=int, default=ParkingAPI.DEFAULT_RADIUS_METERS)
    parser.add_argument("--open-now", action="store_true", help="Only include currently open places")
    parser.add_argument(
        "--api-key", dest="api_key", default=os.getenv("GOOGLE_API_KEY"), help="Google API key"
    )
    args = parser.parse_args()

    if not args.api_key:
        parser.error("Google API key required via --api-key or GOOGLE_API_KEY env var")

    api = ParkingAPI(api_key=args.api_key)
    places = api.nearby(
        args.lat, args.lng, radius=args.radius, open_now=args.open_now
    )
    summaries = [ParkingAPI.summarize(p) for p in places]
    print(json.dumps(summaries, indent=2))
