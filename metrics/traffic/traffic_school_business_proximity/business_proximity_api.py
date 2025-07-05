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
from .business_proximity.services.proximity_service import ProximityService
from .business_proximity.models.proximity_models import (
    ProximitySearchRequest,
    ProximitySearchResponse,
)

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
