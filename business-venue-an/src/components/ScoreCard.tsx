'use client';

import { MetricScore } from '@/types';

interface ScoreCardProps {
  metric: MetricScore;
}

export function ScoreCard({ metric }: ScoreCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{metric.name}</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(metric.score)}`}>
          {metric.score}/100
        </span>
      </div>
      
      <div className="mb-3">
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm text-gray-500">Score</span>
          <span className="text-sm text-gray-500">Weight: {Math.round(metric.weight * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(metric.score)}`}
            style={{ width: `${metric.score}%` }}
          />
        </div>
      </div>
      
      <p className="text-sm text-gray-600">{metric.description}</p>
    </div>
  );
}