'use client';

import { useState } from 'react';
import { BusinessAnalysisForm } from "../src/components/BusinessAnalysisForm"
import { MetricsOverview } from '../src/components//MetricsOverview';
import { CompetitorSection } from '../src/components/CompetitorSection';
import { BusinessAnalysisRequest, BusinessAnalysisResult } from '../src/types';
import { generateMockMetrics, calculateOverallScore } from '../src/services/mockMetrics';

export default function Home() {
  const [analysisResult, setAnalysisResult] = useState<BusinessAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'competitors'>('overview');

  const handleAnalysisSubmit = async (request: BusinessAnalysisRequest) => {
    setLoading(true);
    
    try {
      const metrics = generateMockMetrics(request.businessType, request.location);
      const overallScore = calculateOverallScore(metrics);
      
      const result: BusinessAnalysisResult = {
        overallScore,
        metrics,
        competitors: [], // Will be populated by CompetitorSection
        location: request.location,
        businessType: request.businessType
      };
      
      setAnalysisResult(result);
      setActiveTab('overview');
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartOver = () => {
    setAnalysisResult(null);
    setActiveTab('overview');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {!analysisResult ? (
          <div className="max-w-4xl mx-auto">
            <BusinessAnalysisForm onSubmit={handleAnalysisSubmit} loading={loading} />
          </div>
        ) : (
          <div className="max-w-7xl mx-auto">
            {/* Header with tabs */}
            <div className="bg-white rounded-lg shadow-sm mb-6 p-6">
              <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold text-gray-900">Business Analysis Results</h1>
                <button
                  onClick={handleStartOver}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Start New Analysis
                </button>
              </div>
              
              <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'overview'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Overview & Metrics
                </button>
                <button
                  onClick={() => setActiveTab('competitors')}
                  className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'competitors'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Competitors
                </button>
              </div>
            </div>

            {/* Tab Content */}
            <div className="transition-all duration-300">
              {activeTab === 'overview' ? (
                <MetricsOverview
                  metrics={analysisResult.metrics}
                  overallScore={analysisResult.overallScore}
                  businessType={analysisResult.businessType}
                  location={analysisResult.location}
                />
              ) : (
                <CompetitorSection
                  businessType={analysisResult.businessType}
                  location={analysisResult.location}
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
