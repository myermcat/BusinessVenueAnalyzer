'use client';

import { MetricScore } from '@/types';
import { ScoreCard } from './ScoreCard';

interface MetricsOverviewProps {
  metrics: MetricScore[];
  overallScore: number;
  businessType: string;
  location: string;
}

export function MetricsOverview({ metrics, overallScore, businessType, location }: MetricsOverviewProps) {
  const getOverallScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100 border-green-200';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100 border-yellow-200';
    return 'text-red-600 bg-red-100 border-red-200';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Improvement';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Analysis Results for {businessType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </h2>
        <p className="text-gray-600 mb-4">Location: {location}</p>
        
        {/* Overall Score */}
        <div className={`inline-flex items-center px-6 py-3 rounded-lg border-2 ${getOverallScoreColor(overallScore)}`}>
          <div className="text-center">
            <div className="text-3xl font-bold">{overallScore}/100</div>
            <div className="text-sm font-medium">{getScoreLabel(overallScore)}</div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metrics.map((metric, index) => (
          <ScoreCard key={index} metric={metric} />
        ))}
      </div>

      {/* Summary */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Summary</h3>
        <div className="space-y-2">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Total Metrics Analyzed:</span> {metrics.length}
          </p>
          <p className="text-sm text-gray-600">
            <span className="font-medium">Best Performing:</span> {
              metrics.reduce((best, current) => 
                current.score > best.score ? current : best
              ).name
            }
          </p>
          <p className="text-sm text-gray-600">
            <span className="font-medium">Areas for Improvement:</span> {
              metrics
                .filter(m => m.score < 60)
                .map(m => m.name)
                .join(', ') || 'None'
            }
          </p>
        </div>
      </div>
    </div>
  );
}