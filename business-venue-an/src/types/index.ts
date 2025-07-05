export interface BusinessAnalysisRequest {
  businessType: string;
  location: string;
}

export interface MetricScore {
  name: string;
  score: number;
  weight: number;
  description: string;
}

export interface BusinessAnalysisResult {
  overallScore: number;
  metrics: MetricScore[];
  competitors: Competitor[];
  location: string;
  businessType: string;
}

export interface OpeningHours {
  open_now: boolean;
  periods?: any[];
  weekday_text?: string[];
}

export interface Review {
  author_name: string;
  rating: number;
  text: string;
  time?: string;
}

export interface Competitor {
  name: string;
  address: string;
  rating?: number;
  review_count?: number;
  price_level?: string;
  phone?: string;
  website?: string;
  business_status?: string;
  opening_hours?: OpeningHours;
  top_reviews: Review[];
  place_id: string;
  competitor_analysis?: string;
  data_sources: string[];
  analysis_confidence?: number;
}

export interface QueryInfo {
  business_type: string;
  location: string;
  search_query: string;
  radius_meters: number;
  timestamp: string;
  total_results: number;
}

export interface MarketInsights {
  average_rating?: number;
  rating_distribution: { [key: string]: number };
  price_level_distribution: { [key: string]: number };
  total_reviews: number;
  highly_rated_count: number;
  market_saturation: string;
}

export interface CompetitorAnalysisRequest {
  business_type: string;
  location: string;
  radius_meters?: number;
  max_results?: number;
  min_rating?: number;
  open_now?: boolean;
  enable_deep_analysis?: boolean;
}

export interface CompetitorAnalysisResponse {
  query_info: QueryInfo;
  competitors: Competitor[];
  market_insights: MarketInsights;
}