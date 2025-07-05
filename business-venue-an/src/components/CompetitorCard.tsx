'use client';

import { useState } from 'react';
import { Competitor } from '@/types';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';

interface CompetitorCardProps {
  competitor: Competitor;
}

export function CompetitorCard({ competitor }: CompetitorCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getRatingColor = (rating?: number) => {
    if (!rating) return 'text-gray-600 bg-gray-100';
    if (rating >= 4.5) return 'text-green-600 bg-green-100';
    if (rating >= 4.0) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getPriceLevelText = (priceLevel?: string) => {
    if (!priceLevel) return 'N/A';
    return priceLevel;
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">{competitor.name}</h3>
            <p className="text-sm text-gray-600">{competitor.address}</p>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRatingColor(competitor.rating)}`}>
              ⭐ {competitor.rating?.toFixed(1) || 'N/A'}
            </span>
            {competitor.business_status && (
              <span className="text-xs text-gray-500">
                {competitor.business_status}
              </span>
            )}
          </div>
        </div>

        {/* Quick Info */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex space-x-4 text-sm text-gray-600">
            <span>{competitor.review_count || 0} reviews</span>
            <span>Price: {getPriceLevelText(competitor.price_level)}</span>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            {isExpanded ? 'Less Info' : 'More Info'}
            {isExpanded ? (
              <ChevronUpIcon className="ml-1 h-4 w-4" />
            ) : (
              <ChevronDownIcon className="ml-1 h-4 w-4" />
            )}
          </button>
        </div>

        {/* Expandable Details */}
        {isExpanded && (
          <div className="border-t pt-4 space-y-3">
            {competitor.opening_hours && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Hours</h4>
                <div className="text-sm text-gray-600">
                  <p className={`mb-1 ${competitor.opening_hours.open_now ? 'text-green-600' : 'text-red-600'}`}>
                    {competitor.opening_hours.open_now ? 'Open Now' : 'Closed'}
                  </p>
                  {competitor.opening_hours.weekday_text && (
                    <div className="space-y-1">
                      {competitor.opening_hours.weekday_text.slice(0, 3).map((day, index) => (
                        <p key={index} className="text-xs">{day}</p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {competitor.phone && (
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Phone</h4>
                <p className="text-sm text-gray-600">{competitor.phone}</p>
              </div>
            )}

            {competitor.website && (
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Website</h4>
                <a 
                  href={competitor.website} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Visit Website
                </a>
              </div>
            )}

            {competitor.competitor_analysis && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Analysis</h4>
                <p className="text-sm text-gray-600">{competitor.competitor_analysis}</p>
              </div>
            )}

            {competitor.top_reviews && competitor.top_reviews.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Recent Reviews</h4>
                <div className="space-y-2">
                  {competitor.top_reviews.slice(0, 2).map((review, index) => (
                    <div key={index} className="bg-gray-50 p-3 rounded">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-sm font-medium text-gray-900">{review.author_name}</span>
                        <span className="text-xs text-yellow-600">⭐ {review.rating}</span>
                      </div>
                      <p className="text-xs text-gray-600 line-clamp-2">{review.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}