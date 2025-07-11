'use client';

import { useState } from 'react';
import { BusinessAnalysisRequest } from '@/types';

interface BusinessAnalysisFormProps {
  onSubmit: (request: BusinessAnalysisRequest) => void;
  loading?: boolean;
}

const businessTypes = [
  { value: 'restaurant_cafe', label: 'Restaurant/Cafe' },
  { value: 'office_clinic', label: 'Office/Clinic' },
  { value: 'boutique_storefront', label: 'Boutique/Storefront' },
  { value: 'studio_gym', label: 'Studio/Gym' },
  { value: 'services', label: 'Services' },
];

export function BusinessAnalysisForm({ onSubmit, loading = false }: BusinessAnalysisFormProps) {
  const [businessType, setBusinessType] = useState('');
  const [location, setLocation] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (businessType && location) {
      onSubmit({ businessType, location });
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 rounded-lg shadow-lg" style={{backgroundColor: '#FDF1C9'}}>
      <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center flex items-center justify-center gap-2">
        <img src="/logo.jpg" alt="Sprout Point Logo" style={{ width: 40, height: 40 }} className="inline-block" />
        Sprout Point
      </h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="businessType" className="block text-sm font-medium text-gray-700 mb-2">
            Business Type
          </label>
          <select
            id="businessType"
            value={businessType}
            onChange={(e) => setBusinessType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Select a business type</option>
            {businessTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter address or city (e.g., downtown Ottawa, 123 Main St)"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading || !businessType || !location}
          className="w-full bg-[#0F3E69] text-white py-2 px-4 rounded-md hover:bg-[#0A2B4D] focus:outline-none focus:ring-2 focus:ring-[#0F3E69] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Analyzing...' : 'Analyze Location'}
        </button>
      </form>
    </div>
  );
}