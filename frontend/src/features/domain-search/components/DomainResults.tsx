import React from 'react';
import type { DomainSearchResult } from '../types';
import { WhoisResultCard } from './WhoisResultCard';

interface DomainResultsProps {
  results: DomainSearchResult[];
  loading?: boolean;
  error?: string | null;
  onSelect?: (domain: string) => void;
  className?: string;
}

// Helper component for displaying score bars
const ScoreBar: React.FC<{ value: number; max?: number; color?: string }> = ({
  value,
  max = 10,
  color = 'blue',
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  }[color] || 'bg-blue-500';

  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5">
      <div 
        className={`h-2.5 rounded-full ${colorClasses}`}
        style={{ width: `${percentage}%` }}
      ></div>
    </div>
  );
};

// Helper component for displaying brand archetype badges
const BrandArchetypeBadge: React.FC<{ 
  archetype: string; 
  confidence: number 
}> = ({ archetype, confidence }) => {
  const colorMap: Record<string, string> = {
    'The Hero': 'bg-red-100 text-red-800',
    'The Sage': 'bg-blue-100 text-blue-800',
    'The Explorer': 'bg-green-100 text-green-800',
    'The Creator': 'bg-purple-100 text-purple-800',
    'The Caregiver': 'bg-pink-100 text-pink-800',
  };

  const defaultColor = 'bg-gray-100 text-gray-800';
  const colorClass = colorMap[archetype] || defaultColor;
  
  return (
    <div className="flex items-center">
      <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${colorClass}`}>
        {archetype}
      </span>
      <span className="ml-2 text-xs text-gray-500">
        {Math.round(confidence * 100)}% match
      </span>
    </div>
  );
};

export const DomainResults: React.FC<DomainResultsProps> = ({
  results,
  loading = false,
  error = null,
  onSelect,
  className = '',
}) => {
  if (loading) {
    return (
      <div className={`flex flex-col items-center justify-center p-12 ${className}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-gray-600">Analyzing domains...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-6 bg-red-50 border border-red-200 rounded-lg ${className}`}>
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading results</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className={`p-8 text-center ${className}`}>
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No domains found</h3>
        <p className="mt-1 text-sm text-gray-500">
          Try adjusting your search or filter to find what you're looking for.
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Domain Search Results
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            AI-powered domain analysis to help you find the perfect name
          </p>
        </div>
        
        <div className="divide-y divide-gray-200">
          {results.map((result, index) => {
            const domainParts = result.domain.split('.');
            const domainName = domainParts[0];
            const domainTld = domainParts.slice(1).join('.');
            
            return (
              <div 
                key={`${result.domain}-${index}`}
                className={`px-4 py-5 sm:px-6 hover:bg-gray-50 transition-colors ${
                  result.is_available ? 'cursor-pointer' : 'opacity-75'
                }`}
                onClick={() => result.is_available && onSelect?.(result.domain)}
              >
                <div className="flex flex-col">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <div className="text-lg font-medium text-gray-900">
                        <span className="font-bold">{domainName}</span>
                        <span className="text-gray-500">.{domainTld}</span>
                      </div>
                      
                      <div className="ml-4 flex-shrink-0">
                        {result.is_available ? (
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Available
                          </span>
                        ) : (
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Taken
                          </span>
                        )}
                        
                        {result.is_premium && (
                          <span className="ml-2 px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            Premium
                          </span>
                        )}
                      </div>
                    </div>
                    
                    {result.is_available && (
                      <div className="text-right">
                        {result.price ? (
                          <>
                            <span className="text-2xl font-bold text-gray-900">
                              ${result.price}
                            </span>
                            <span className="text-sm text-gray-500 ml-1">/year</span>
                          </>
                        ) : (
                          <span className="text-green-600 font-medium">
                            Register
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Show WHOIS info if available */}
                  {result.whois_data && (
                    <div className="mt-3 border-t border-gray-100 pt-3">
                      <WhoisResultCard result={result} className="shadow-none border border-gray-200" />
                    </div>
                  )}
                </div>
                
                {/* AI Analysis Section */}
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Linguistic Analysis */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 mb-2">LINGUISTIC ANALYSIS</h4>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Quality Score</span>
                            <span className="font-medium">
                              {result.analysis.linguistic.score.toFixed(1)}/10
                            </span>
                          </div>
                          <ScoreBar 
                            value={result.analysis.linguistic.score} 
                            color={
                              result.analysis.linguistic.score >= 8 ? 'green' : 
                              result.analysis.linguistic.score >= 5 ? 'blue' : 'yellow'
                            }
                          />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <div className="text-sm text-gray-500 mb-1">Pronounceable</div>
                            <div className="text-sm font-medium">
                              {result.analysis.linguistic.is_pronounceable ? 'Yes' : 'No'}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm text-gray-500 mb-1">Syllables</div>
                            <div className="text-sm font-medium">
                              {result.analysis.linguistic.syllable_count}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Brand Analysis */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 mb-2">BRAND ANALYSIS</h4>
                      <div className="space-y-4">
                        <div>
                          <div className="text-sm text-gray-500 mb-1">Archetype</div>
                          <BrandArchetypeBadge 
                            archetype={result.analysis.brand_archetype}
                            confidence={result.analysis.brand_confidence}
                          />
                        </div>
                        
                        <div>
                          <div className="text-sm text-gray-500 mb-1">Trademark Risk</div>
                          <div className="flex items-center">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              result.analysis.trademark_risk === 'low' ? 'bg-green-100 text-green-800' :
                              result.analysis.trademark_risk === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {result.analysis.trademark_risk.charAt(0).toUpperCase() + result.analysis.trademark_risk.slice(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
