import React, { useState } from 'react';
import { DomainSearch } from './DomainSearch';
import { DomainResults } from './DomainResults';
import type { DomainSearchResult } from '../types';

export const DomainSearchPage: React.FC = () => {
  const [results, setResults] = useState<DomainSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchStats] = useState({
    total: 0,
    available: 0,
    taken: 0,
    premium: 0,
  });

  const handleSearchStart = () => {
    setLoading(true);
    setError(null);
    setResults([]);
  };

  const handleSearchComplete = (searchResults: DomainSearchResult[]) => {
    setResults(searchResults);
    setLoading(false);
  };

  const handleSearchError = (errorMessage: string) => {
    setError(errorMessage);
    setLoading(false);
  };

  const handleDomainSelect = (domain: string) => {
    console.log('Selected domain:', domain);
    // Handle domain selection (e.g., navigate to domain details or registration)
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
          Find Your Perfect Domain
        </h1>
        <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
          AI-powered domain search with brand analysis and availability checking
        </p>
      </div>
      
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
        <DomainSearch 
          onSearchStart={handleSearchStart}
          onSearchComplete={handleSearchComplete}
          onSearchError={handleSearchError}
          className="max-w-4xl mx-auto"
        />
      </div>
      
      {!loading && results.length > 0 && (
        <div className="mb-6">
          <div className="flex flex-wrap justify-between items-center bg-white rounded-lg shadow px-6 py-4 border border-gray-200">
            <div className="text-sm text-gray-600">
              Showing <span className="font-medium">{results.length}</span> of{' '}
              <span className="font-medium">{searchStats.total}</span> results
            </div>
            <div className="flex space-x-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{searchStats.available}</div>
                <div className="text-xs text-gray-500">Available</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{searchStats.premium}</div>
                <div className="text-xs text-gray-500">Premium</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{searchStats.taken}</div>
                <div className="text-xs text-gray-500">Taken</div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <DomainResults 
        results={results}
        loading={loading}
        error={error}
        onSelect={handleDomainSelect}
        className="mt-6"
      />
      
      {!loading && results.length === 0 && !error && (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">No domains found</h3>
          <p className="text-gray-500">Try adjusting your search to find more results.</p>
        </div>
      )}
    </div>
  );
};
