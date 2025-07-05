import axios from 'axios';
import { CompetitorAnalysisRequest, CompetitorAnalysisResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export class CompetitorApiService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 50000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async analyzeCompetitors(request: CompetitorAnalysisRequest): Promise<CompetitorAnalysisResponse> {
    try {
      const response = await this.axiosInstance.post<CompetitorAnalysisResponse>(
        '/competitors/analyze',
        request
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`API Error: ${error.response?.data?.detail || error.message}`);
      }
      throw error;
    }
  }

  async healthCheck(): Promise<{ status: string }> {
    try {
      const response = await this.axiosInstance.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('API health check failed');
    }
  }
}

export const competitorApi = new CompetitorApiService();