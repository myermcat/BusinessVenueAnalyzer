import openai
from typing import List, Dict, Any
from models.competitor_models import Competitor, Review, TavilyResponse

class AnalysisService:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    async def generate_competitor_analysis(
        self, 
        competitor: Competitor, 
        tavily_data: TavilyResponse,
        business_type: str,
        location: str
    ) -> Dict[str, Any]:
        
        # Prepare context for LLM
        context = self._build_analysis_context(competitor, tavily_data, business_type, location)
        
        # Generate analysis
        analysis_text = await self._generate_analysis(context)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(competitor, tavily_data)
        
        return {
            "analysis": analysis_text,
            "confidence": confidence,
            "data_sources": [result.url for result in tavily_data.results]
        }
    
    def _build_analysis_context(
        self, 
        competitor: Competitor, 
        tavily_data: TavilyResponse,
        business_type: str,
        location: str
    ) -> str:
        
        # Build comprehensive context
        context_parts = [
            f"Business: {competitor.name}",
            f"Location: {competitor.address}",
            f"Business Type: {business_type} in {location}",
            f"Google Places Data:"
        ]
        
        # Add Places API data
        if competitor.rating:
            context_parts.append(f"- Rating: {competitor.rating}/5.0 ({competitor.review_count} reviews)")
        if competitor.price_level:
            context_parts.append(f"- Price Level: {competitor.price_level}")
        if competitor.phone:
            context_parts.append(f"- Phone: {competitor.phone}")
        if competitor.website:
            context_parts.append(f"- Website: {competitor.website}")
        
        # Add top reviews
        if competitor.top_reviews:
            context_parts.append("- Recent Reviews:")
            for review in competitor.top_reviews[:2]:  # Top 2 reviews
                context_parts.append(f"  * {review.rating}/5: {review.text[:150]}...")
        
        # Add Tavily research
        if tavily_data.ai_answer:
            context_parts.append(f"Web Research Summary: {tavily_data.ai_answer}")
        
        if tavily_data.results:
            context_parts.append("Additional Web Information:")
            for result in tavily_data.results[:3]:  # Top 3 results
                context_parts.append(f"- {result.title}: {result.content[:200]}...")
        
        return "\n".join(context_parts)
    
    async def _generate_analysis(self, context: str) -> str:
        system_prompt = """You are a business analyst specializing in competitive intelligence. 
        
        Analyze the provided competitor data and generate a concise 3-4 sentence competitive analysis that covers:
        1. Market positioning & unique value proposition
        2. Customer sentiment & reputation based on reviews/ratings
        3. Competitive strengths and potential weaknesses
        4. Overall threat level and competitive assessment
        
        Be specific, actionable, and focus on insights that would help a business owner understand this competitor's market position.
        Keep the analysis professional and fact-based."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            # Fallback analysis if LLM fails
            return self._generate_fallback_analysis(context)
    
    def _generate_fallback_analysis(self, context: str) -> str:
        # Simple rule-based analysis as fallback
        lines = context.split('\n')
        business_name = "This competitor"
        
        for line in lines:
            if line.startswith("Business: "):
                business_name = line.split(": ")[1]
                break
        
        rating_info = ""
        for line in lines:
            if "Rating:" in line:
                rating_info = line.strip()
                break
        
        return f"{business_name} appears to be an established competitor in the local market. {rating_info if rating_info else 'Limited rating information available.'} Based on available data, they represent a standard competitive presence that should be monitored for market positioning and customer engagement strategies."
    
    def _calculate_confidence(self, competitor: Competitor, tavily_data: TavilyResponse) -> float:
        confidence_score = 0.0
        
        # Base confidence from Places API data
        if competitor.rating is not None:
            confidence_score += 0.2
        if competitor.review_count and competitor.review_count > 10:
            confidence_score += 0.2
        if competitor.top_reviews:
            confidence_score += 0.1
        if competitor.website:
            confidence_score += 0.1
        
        # Additional confidence from Tavily data
        if tavily_data.ai_answer:
            confidence_score += 0.2
        if tavily_data.results:
            confidence_score += 0.1 * min(len(tavily_data.results), 3) / 3
        
        return min(confidence_score, 1.0)
    
    async def batch_analyze_competitors(
        self, 
        competitors: List[Competitor], 
        tavily_responses: List[TavilyResponse],
        business_type: str,
        location: str
    ) -> List[Competitor]:
        
        enhanced_competitors = []
        
        for competitor, tavily_data in zip(competitors, tavily_responses):
            try:
                analysis_result = await self.generate_competitor_analysis(
                    competitor, tavily_data, business_type, location
                )
                
                # Update competitor with analysis
                competitor.competitor_analysis = analysis_result["analysis"]
                competitor.analysis_confidence = analysis_result["confidence"]
                competitor.data_sources = analysis_result["data_sources"]
                
            except Exception as e:
                # Set fallback values on error
                competitor.competitor_analysis = "Analysis unavailable due to processing error."
                competitor.analysis_confidence = 0.1
                competitor.data_sources = []
            
            enhanced_competitors.append(competitor)
        
        return enhanced_competitors