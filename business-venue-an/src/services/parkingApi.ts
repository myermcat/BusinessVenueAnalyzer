import axios from 'axios';

const API_BASE_URL = 'http://localhost:8002/api/v1';

export interface ParkingAnalysisRequest {
  places_type: string;
  location: string;
  max_results?: number;
  min_rating?: number;
  enable_deep_analysis?: boolean;
}

export interface ParkingPlace {
  name: string;
  address: string;
  rating: number;
  user_ratings_total: number;
  price_level: string;
  place_id: string;
}

export interface QueryInfo {
  location: string;
  place_types: string[];
  timestamp: string;
  max_results: number;
  min_rating: number;
}

export interface DeepAnalysis {
  average_rating: number;
  total_places: number;
}

export interface ParkingAnalysisResponse {
  query_info: QueryInfo;
  results: {
    parking: ParkingPlace[];
  };
  deep_analysis: DeepAnalysis;
}

export class ParkingApiService {
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

  async analyzeParking(request: ParkingAnalysisRequest): Promise<ParkingAnalysisResponse> {
    try {
      const response = await this.axiosInstance.post<ParkingAnalysisResponse>(
        '/business-proximity/analyze',
        request
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Parking API Error: ${error.response?.data?.detail || error.message}`);
      }
      throw error;
    }
  }

  async healthCheck(): Promise<{ status: string }> {
    try {
      const response = await this.axiosInstance.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Parking API health check failed');
    }
  }
}

export const parkingApi = new ParkingApiService();