'use client';

import { useState, useEffect } from 'react';
import { Competitor } from '../types';
import { CompetitorCard } from './CompetitorCard';
import { competitorApi } from '../services/competitorApi';

interface CompetitorSectionProps {
  businessType: string;
  location: string;
}

export function CompetitorSection({ businessType, location }: CompetitorSectionProps) {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    const fetchCompetitors = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await competitorApi.analyzeCompetitors({
          business_type: businessType,
          location: location,
          max_results: 10,
          min_rating: 3.0,
          enable_deep_analysis: true
        });
        
        setCompetitors(response.competitors);
        setSummary(response.market_insights);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch competitors');
      } finally {
        setLoading(false);
      }
    };

    if (businessType && location) {
      fetchCompetitors();
    }
  }, [businessType, location]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-md p-6">
              <div className="animate-pulse">
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-full"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to Load Competitors</h3>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      {summary && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Competitor Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{competitors.length}</div>
              <div className="text-sm text-gray-600">Total Competitors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{summary.average_rating?.toFixed(1) || 'N/A'}</div>
              <div className="text-sm text-gray-600">Average Rating</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{summary.market_saturation}</div>
              <div className="text-sm text-gray-600">Market Saturation</div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="text-center">
              <div className="text-xl font-bold text-orange-600">{summary.total_reviews}</div>
              <div className="text-sm text-gray-600">Total Reviews</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-indigo-600">{summary.highly_rated_count}</div>
              <div className="text-sm text-gray-600">Highly Rated (4.0+)</div>
            </div>
          </div>
        </div>
      )}

      {/* Competitors Grid */}
      {competitors.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {competitors.map((competitor, index) => (
            <CompetitorCard key={competitor.place_id || index} competitor={competitor} />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="text-gray-500 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-6m-2-5.5v5.5m8 0V9a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2h14a2 2 0 002-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Competitors Found</h3>
          <p className="text-sm text-gray-600">
            We couldn't find any competitors in this area. This could be a great opportunity for your business!
          </p>
        </div>
      )}
    </div>
  );
}