import { MetricScore } from '@/types';
import { censusApi, CensusAnalysisResponse } from './censusApi';
import { parkingApi, ParkingAnalysisResponse } from './parkingApi';
import { competitorCountApi, CompetitorCountResponse } from './competitorCountApi';

const metricsMap = {
  "restaurant_cafe": {
    "foot_traffic": 0.3,
    "competitor_count": 0.25,
    "local_income": 0.2,
    "dwelling_value": 0.15,
    "parking_availability": 0.1
  },
  "office_clinic": {
    "rent_cost": 0.3,
    "local_income": 0.25,
    "dwelling_value": 0.2,
    "parking_availability": 0.15,
    "public_transit_access": 0.1
  },
  "boutique_storefront": {
    "foot_traffic": 0.25,
    "local_income": 0.25,
    "dwelling_value": 0.2,
    "visibility_from_street": 0.15,
    "nearby_shops": 0.15
  },
  "studio_gym": {
    "population_density": 0.3,
    "local_income": 0.25,
    "dwelling_value": 0.2,
    "accessibility": 0.15,
    "noise_tolerance_zone": 0.1
  },
  "services": {
    "local_income": 0.3,
    "dwelling_value": 0.25,
    "low_crime_rate": 0.2,
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
  "dwelling_value": "Average property values in the neighborhood",
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

export async function generateMetricsWithCensusData(businessType: string, location: string): Promise<MetricScore[]> {
  const businessKey = businessType.toLowerCase().replace(/\s+/g, '_');
  const weights = metricsMap[businessKey as keyof typeof metricsMap] || metricsMap.restaurant_cafe;
  
  const metrics: MetricScore[] = [];
  let censusData: CensusAnalysisResponse | null = null;
  let parkingData: ParkingAnalysisResponse | null = null;
  let competitorCountData: CompetitorCountResponse | null = null;
  
  // Try to get real census data
  try {
    censusData = await censusApi.analyzeDemographics({
      address: location,
      walking_radius_km: 1.0,
      driving_radius_km: 3.0
    });
  } catch (error) {
    console.warn('Failed to fetch census data, using mock data:', error);
  }
  
  // Try to get real parking data
  try {
    parkingData = await parkingApi.analyzeParking({
      places_type: 'parking',
      location: location,
      max_results: 10,
      min_rating: 3.0,
      enable_deep_analysis: true
    });
  } catch (error) {
    console.warn('Failed to fetch parking data, using mock data:', error);
  }
  
  // Try to get competitor count data
  try {
    competitorCountData = await competitorCountApi.countCompetitors({
      business_type: businessType,
      location: location,
      max_results: 20,
      min_rating: 0.0
    });
  } catch (error) {
    console.warn('Failed to fetch competitor count data, using mock data:', error);
  }
  
  for (const [metricName, weight] of Object.entries(weights)) {
    let score: number;
    let description = metricDescriptions[metricName] || `Analysis for ${metricName.replace(/_/g, ' ')}`;
    
    // Use real census data for specific metrics, fallback to mock for others
    if (censusData && metricName === 'local_income') {
      // Map median income to a 0-100 score
      const income = censusData.walking_radius.avg_median_income;
      score = Math.min(100, Math.max(0, (income / 100000) * 100)); // Normalize to $100k = 100 points
      description = `${metricDescriptions[metricName]} | Median Income: $${income.toLocaleString()}`;
    } else if (censusData && metricName === 'dwelling_value') {
      // Map dwelling value to a 0-100 score
      const dwellingValue = censusData.walking_radius.avg_median_dwelling_value;
      score = Math.min(100, Math.max(0, (dwellingValue / 800000) * 100)); // Normalize to $800k = 100 points
      description = `${metricDescriptions[metricName]} | Median Home Value: $${dwellingValue.toLocaleString()}`;
    } else if (censusData && metricName === 'foot_traffic') {
      // Map population density to foot traffic score
      const density = censusData.walking_radius.avg_population_density;
      score = Math.min(100, Math.max(0, (density / 5000) * 100)); // Normalize to 5000/km² = 100 points
      description = `${metricDescriptions[metricName]} | Population Density: ${density.toLocaleString()} people/km²`;
    } else if (censusData && metricName === 'population_density') {
      // Direct population density mapping
      const density = censusData.walking_radius.avg_population_density;
      score = Math.min(100, Math.max(0, (density / 5000) * 100)); // Normalize to 5000/km² = 100 points
      description = `${metricDescriptions[metricName]} | Population Density: ${density.toLocaleString()} people/km²`;
    } else if (parkingData && metricName === 'parking_availability') {
      // Map parking data to availability score
      const totalParkingSpots = parkingData.results.parking.length;
      const avgRating = parkingData.deep_analysis.average_rating;
      
      // Score based on number of parking spots (0-10 = 0-60 points) + quality (rating 0-5 = 0-40 points)
      const availabilityScore = Math.min(60, (totalParkingSpots / 10) * 60);
      const qualityScore = Math.min(40, (avgRating / 5) * 40);
      score = Math.round(availabilityScore + qualityScore);
      
      description = `${metricDescriptions[metricName]} | Found ${totalParkingSpots} parking locations | Avg Rating: ${avgRating.toFixed(1)}/5.0`;
    } else if (competitorCountData && metricName === 'competitor_count') {
      // Map competitor count to competition intensity score
      const competitorCount = competitorCountData.competitor_count;
      
      // Inverse scoring: fewer competitors = higher score (better for business)
      // 0 competitors = 100 points, 20+ competitors = 10 points
      if (competitorCount === 0) {
        score = 100;
      } else {
        score = Math.max(10, 100 - (competitorCount * 4.5)); // Linear decrease
      }
      
      description = `${metricDescriptions[metricName]} | Found ${competitorCount} direct competitors in the area`;
    } else {
      // Use mock data for other metrics
      const baseScore = Math.random() * 40 + 40;
      const locationModifier = location.toLowerCase().includes('downtown') ? 10 : 0;
      const businessModifier = businessType.toLowerCase().includes('cafe') ? 5 : 0;
      score = Math.min(100, Math.max(0, baseScore + locationModifier + businessModifier));
      description = `${description} | Estimated based on location factors`;
    }
    
    metrics.push({
      name: metricName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      score: Math.round(score),
      weight: weight,
      description: description
    });
  }
  
  return metrics;
}

export function calculateOverallScore(metrics: MetricScore[]): number {
  const weightedSum = metrics.reduce((sum, metric) => sum + (metric.score * metric.weight), 0);
  return Math.round(weightedSum);
}