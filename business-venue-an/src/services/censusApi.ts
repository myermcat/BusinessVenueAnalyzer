import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

export interface CensusAnalysisRequest {
  address?: string;
  latitude?: number;
  longitude?: number;
  walking_radius_km?: number;
  driving_radius_km?: number;
  include_detailed_areas?: boolean;
}

export interface LocationInfo {
  latitude: number;
  longitude: number;
}

export interface RadiiInfo {
  walking_km: number;
  driving_km: number;
}

export interface RadiusStats {
  total_population: number;
  num_areas: number;
  avg_population_density: number;
  avg_median_income: number;
  avg_median_dwelling_value: number;
  avg_age: number;
  avg_household_size: number;
  total_households: number;
  total_dwellings: number;
  total_area_km2: number;
}

export interface CensusAnalysisResponse {
  location: LocationInfo;
  radii: RadiiInfo;
  walking_radius: RadiusStats;
  driving_radius: RadiusStats;
  address_validation?: {
    original_address?: string;
    validated_address?: string;
    confidence?: string;
    coordinates_source: string;
  };
}

export class CensusApiService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async analyzeDemographics(request: CensusAnalysisRequest): Promise<CensusAnalysisResponse> {
    try {
      const response = await this.axiosInstance.post<CensusAnalysisResponse>(
        '/census/analyze',
        request
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Census API Error: ${error.response?.data?.detail || error.message}`);
      }
      throw error;
    }
  }

  async healthCheck(): Promise<{ status: string; census_processor_available: boolean; address_validator_available: boolean }> {
    try {
      const response = await this.axiosInstance.get('/census/health');
      return response.data;
    } catch (error) {
      throw new Error('Census API health check failed');
    }
  }
}

export const censusApi = new CensusApiService();