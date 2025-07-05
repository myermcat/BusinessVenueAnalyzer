import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface CompetitorCountRequest {
  business_type: string;
  location: string;
  max_results?: number;
  min_rating?: number;
}

export interface CompetitorCountResponse {
  competitor_count: number;
  business_type: string;
  location: string;
  search_query: string;
}

export class CompetitorCountApiService {
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

  async countCompetitors(request: CompetitorCountRequest): Promise<CompetitorCountResponse> {
    try {
      const response = await this.axiosInstance.post<CompetitorCountResponse>(
        '/competitors/count',
        request
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Competitor Count API Error: ${error.response?.data?.detail || error.message}`);
      }
      throw error;
    }
  }
}

export const competitorCountApi = new CompetitorCountApiService();