import httpx
import asyncio
from typing import List, Dict, Any
from models.competitor_models import TavilyResponse, TavilySearchResult

class TavilyService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
        
    async def search_competitor(self, competitor_name: str, location: str) -> TavilyResponse:
        query = f"{competitor_name} {location} reviews reputation business"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "query": query,
            "search_depth": "basic",
            "max_results": 4,
            "include_answer": True,
            "topic": "general"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_response(data)
    
    def _parse_response(self, data: Dict[str, Any]) -> TavilyResponse:
        results = []
        
        for result in data.get("results", []):
            search_result = TavilySearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", ""),
                score=result.get("score", 0.0)
            )
            results.append(search_result)
        
        return TavilyResponse(
            query=data.get("query", ""),
            ai_answer=data.get("answer"),
            results=results
        )
    
    async def batch_search_competitors(self, competitors: List[Dict[str, str]]) -> List[TavilyResponse]:
        tasks = []
        
        for competitor in competitors:
            task = self.search_competitor(
                competitor["name"], 
                competitor["location"]
            )
            tasks.append(task)
        
        # Execute searches concurrently with rate limiting
        responses = []
        batch_size = 3  # Limit concurrent requests
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_responses = await asyncio.gather(*batch, return_exceptions=True)
            
            for response in batch_responses:
                if isinstance(response, Exception):
                    # Return empty response on error
                    responses.append(TavilyResponse(query="", results=[]))
                else:
                    responses.append(response)
            
            # Rate limiting pause between batches
            if i + batch_size < len(tasks):
                await asyncio.sleep(1)
        
        return responses