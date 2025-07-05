import { MetricScore } from '@/types';

const metricsMap = {
  "restaurant_cafe": {
    "foot_traffic": 0.35,
    "competitor_count": 0.3,
    "school_business_proximity": 0.2,
    "parking_availability": 0.1,
    "local_income": 0.05
  },
  "office_clinic": {
    "rent_cost": 0.4,
    "quiet_zone": 0.3,
    "parking_availability": 0.2,
    "public_transit_access": 0.1
  },
  "boutique_storefront": {
    "visibility_from_street": 0.3,
    "walkability": 0.25,
    "foot_traffic": 0.2,
    "nearby_shops": 0.15,
    "aesthetic_quality": 0.1
  },
  "studio_gym": {
    "floor_space_estimate": 0.4,
    "noise_tolerance_zone": 0.2,
    "population_density": 0.2,
    "accessibility": 0.2
  },
  "services": {
    "low_crime_rate": 0.3,
    "reputation_area_score": 0.25,
    "nearby_complementary_services": 0.2,
    "commute_accessibility": 0.15,
    "parking_availability": 0.1
  }
};

const metricDescriptions: { [key: string]: string } = {
  "foot_traffic": "Pedestrian activity and potential customer flow",
  "competitor_count": "Number of similar businesses in the area",
  "school_business_proximity": "Distance to educational institutions",
  "parking_availability": "Available parking spaces for customers",
  "local_income": "Average household income in the area",
  "rent_cost": "Commercial rental prices in the location",
  "quiet_zone": "Noise levels and peaceful environment",
  "public_transit_access": "Proximity to public transportation",
  "visibility_from_street": "How visible the location is from main roads",
  "walkability": "Pedestrian-friendly infrastructure",
  "nearby_shops": "Complementary businesses in the vicinity",
  "aesthetic_quality": "Visual appeal of the neighborhood",
  "floor_space_estimate": "Available space for business operations",
  "noise_tolerance_zone": "Suitability for noise-generating activities",
  "population_density": "Number of potential customers in the area",
  "accessibility": "Ease of access for people with disabilities",
  "low_crime_rate": "Safety and security of the location",
  "reputation_area_score": "Overall reputation of the neighborhood",
  "nearby_complementary_services": "Related services that could drive traffic",
  "commute_accessibility": "Ease of commuting to the location"
};

export function generateMockMetrics(businessType: string, location: string): MetricScore[] {
  const businessKey = businessType.toLowerCase().replace(/\s+/g, '_');
  const weights = metricsMap[businessKey as keyof typeof metricsMap] || metricsMap.restaurant_cafe;
  
  const metrics: MetricScore[] = [];
  
  for (const [metricName, weight] of Object.entries(weights)) {
    const baseScore = Math.random() * 40 + 40; // Random score between 40-80
    const locationModifier = location.toLowerCase().includes('downtown') ? 10 : 0;
    const businessModifier = businessType.toLowerCase().includes('cafe') ? 5 : 0;
    
    const score = Math.min(100, Math.max(0, baseScore + locationModifier + businessModifier));
    
    metrics.push({
      name: metricName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      score: Math.round(score),
      weight: weight,
      description: metricDescriptions[metricName] || `Analysis for ${metricName.replace(/_/g, ' ')}`
    });
  }
  
  return metrics;
}

export function calculateOverallScore(metrics: MetricScore[]): number {
  const weightedSum = metrics.reduce((sum, metric) => sum + (metric.score * metric.weight), 0);
  return Math.round(weightedSum);
}