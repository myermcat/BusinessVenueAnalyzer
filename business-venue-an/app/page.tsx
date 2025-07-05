'use client';

import { useState } from 'react';
import { BusinessAnalysisForm } from "../src/components/BusinessAnalysisForm"
import { MetricsOverview } from '../src/components//MetricsOverview';
import { CompetitorSection } from '../src/components/CompetitorSection';
import { BusinessAnalysisRequest, BusinessAnalysisResult, Competitor, MarketInsights } from '../src/types';
import { generateMetricsWithCensusData, calculateOverallScore } from '../src/services/mockMetrics';
import { competitorApi } from '../src/services/competitorApi';

export default function Home() {
  const [analysisResult, setAnalysisResult] = useState<BusinessAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'competitors'>('overview');
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [marketInsights, setMarketInsights] = useState<MarketInsights | null>(null);
  const [competitorLoading, setCompetitorLoading] = useState(false);
  const [competitorError, setCompetitorError] = useState<string | null>(null);

  const handleAnalysisSubmit = async (request: BusinessAnalysisRequest) => {
    setLoading(true);
    setCompetitorLoading(true);
    setCompetitorError(null);
    
    try {
      // Generate metrics with real census data
      const metrics = await generateMetricsWithCensusData(request.businessType, request.location);
      const overallScore = calculateOverallScore(metrics);
      
      // Set initial result with metrics
      const result: BusinessAnalysisResult = {
        overallScore,
        metrics,
        competitors: [],
        location: request.location,
        businessType: request.businessType
      };
      
      setAnalysisResult(result);
      setActiveTab('overview');
      setLoading(false);
      
      // Fetch competitors in background
      try {
        const competitorResponse = await competitorApi.analyzeCompetitors({
          business_type: request.businessType,
          location: request.location,
          max_results: 10,
          min_rating: 3.0,
          enable_deep_analysis: true
        });
        
        setCompetitors(competitorResponse.competitors);
        setMarketInsights(competitorResponse.market_insights);
      } catch (competitorError) {
        setCompetitorError(competitorError instanceof Error ? competitorError.message : 'Failed to fetch competitors');
      } finally {
        setCompetitorLoading(false);
      }
      
    } catch (error) {
      console.error('Analysis failed:', error);
      setLoading(false);
      setCompetitorLoading(false);
    }
  };

  const handleStartOver = () => {
    setAnalysisResult(null);
    setActiveTab('overview');
    setCompetitors([]);
    setMarketInsights(null);
    setCompetitorLoading(false);
    setCompetitorError(null);
  };

  return (
    <div className="relative min-h-screen w-full">
      {/* Full-page background image */}
      <div
        className="fixed inset-0 z-0 bg-cover bg-center"
        style={{ backgroundImage: "url('/business-bg.jpg')" }}
        aria-hidden="true"
      />

      <div className="relative z-20 container mx-auto px-4 py-8">
        {!analysisResult ? (
          <div className="max-w-4xl mx-auto">
            <BusinessAnalysisForm onSubmit={handleAnalysisSubmit} loading={loading} />
          </div>
        ) : (
          <div className="max-w-7xl mx-auto">
            {/* Header with tabs */}
            <div className="bg-white rounded-lg shadow-sm mb-6 p-6" style={{ opacity: 0.95 }}>
              <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold text-gray-900">Sprout Point</h1>
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
                  competitors={competitors}
                  marketInsights={marketInsights}
                  loading={competitorLoading}
                  error={competitorError}
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
