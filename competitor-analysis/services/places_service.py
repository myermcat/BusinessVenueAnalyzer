import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from models.competitor_models import (
    CompetitorAnalysisRequest, 
    CompetitorAnalysisResponse,
    Competitor,
    QueryInfo,
    MarketInsights,
    OpeningHours,
    Review
)

class PlacesService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1/places:searchText"
        
    async def analyze_competitors(self, request: CompetitorAnalysisRequest) -> CompetitorAnalysisResponse:
        search_query = f"{request.business_type} in {request.location}"
        
        places_data = await self._search_places(
            query=search_query,
            max_results=request.max_results,
            min_rating=request.min_rating,
            open_now=request.open_now
        )
        
        competitors = self._parse_competitors(places_data)
        market_insights = self._generate_market_insights(competitors)
        
        query_info = QueryInfo(
            business_type=request.business_type,
            location=request.location,
            search_query=search_query,
            radius_meters=request.radius_meters,
            timestamp=datetime.now(),
            total_results=len(competitors)
        )
        
        return CompetitorAnalysisResponse(
            query_info=query_info,
            competitors=competitors,
            market_insights=market_insights
        )
    
    async def _search_places(self, query: str, max_results: int, min_rating: float, open_now: bool) -> List[Dict]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.businessStatus,places.websiteUri,places.nationalPhoneNumber,places.regularOpeningHours,places.reviews,places.id"
        }
        
        payload = {
            "textQuery": query,
            "pageSize": min(max_results, 20),
            "minRating": min_rating,
            "openNow": open_now
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return data.get("places", [])
    
    def _parse_competitors(self, places_data: List[Dict]) -> List[Competitor]:
        competitors = []
        
        for place in places_data:
            competitor = Competitor(
                name=place.get("displayName", {}).get("text", "Unknown"),
                address=place.get("formattedAddress", ""),
                rating=place.get("rating"),
                review_count=place.get("userRatingCount"),
                price_level=self._parse_price_level(place.get("priceLevel")),
                phone=place.get("nationalPhoneNumber"),
                website=place.get("websiteUri"),
                business_status=place.get("businessStatus"),
                opening_hours=self._parse_opening_hours(place.get("regularOpeningHours")),
                top_reviews=self._parse_reviews(place.get("reviews", [])),
                place_id=place.get("id", "")
            )
            competitors.append(competitor)
        
        return competitors
    
    def _parse_price_level(self, price_level: str) -> str:
        price_mapping = {
            "PRICE_LEVEL_FREE": "Free",
            "PRICE_LEVEL_INEXPENSIVE": "$",
            "PRICE_LEVEL_MODERATE": "$$",
            "PRICE_LEVEL_EXPENSIVE": "$$$",
            "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$"
        }
        return price_mapping.get(price_level, "Unknown")
    
    def _parse_opening_hours(self, hours_data: Dict) -> OpeningHours:
        if not hours_data:
            return None
            
        return OpeningHours(
            open_now=hours_data.get("openNow", False),
            periods=hours_data.get("periods", []),
            weekday_text=hours_data.get("weekdayText", [])
        )
    
    def _parse_reviews(self, reviews_data: List[Dict]) -> List[Review]:
        reviews = []
        
        for review in reviews_data[:3]:  # Top 3 reviews
            review_obj = Review(
                author_name=review.get("authorAttribution", {}).get("displayName", "Anonymous"),
                rating=review.get("rating", 0),
                text=review.get("text", {}).get("text", ""),
                time=None  # Would need to parse publishTime if needed
            )
            reviews.append(review_obj)
        
        return reviews
    
    def _generate_market_insights(self, competitors: List[Competitor]) -> MarketInsights:
        if not competitors:
            return MarketInsights(total_reviews=0, highly_rated_count=0)
        
        ratings = [c.rating for c in competitors if c.rating is not None]
        review_counts = [c.review_count for c in competitors if c.review_count is not None]
        price_levels = [c.price_level for c in competitors if c.price_level and c.price_level != "Unknown"]
        
        # Calculate average rating
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Rating distribution
        rating_dist = {}
        for rating in ratings:
            if rating:
                range_key = f"{int(rating)}-{int(rating)+1}"
                rating_dist[range_key] = rating_dist.get(range_key, 0) + 1
        
        # Price level distribution
        price_dist = {}
        for price in price_levels:
            price_dist[price] = price_dist.get(price, 0) + 1
        
        # Market saturation assessment
        total_competitors = len(competitors)
        if total_competitors >= 15:
            saturation = "High"
        elif total_competitors >= 8:
            saturation = "Medium"
        else:
            saturation = "Low"
        
        return MarketInsights(
            average_rating=avg_rating,
            rating_distribution=rating_dist,
            price_level_distribution=price_dist,
            total_reviews=sum(review_counts),
            highly_rated_count=len([r for r in ratings if r >= 4.0]),
            market_saturation=saturation
        )