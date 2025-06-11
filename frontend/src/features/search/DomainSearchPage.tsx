import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DomainSearch } from '../domain-search/components/DomainSearch';
import type { DomainSearchResult, SearchFilters } from '../domain-search/types';

const DomainSearchPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<DomainSearchResult[]>([]);
  const [query, setQuery] = useState('');
  const [selectedTlds, setSelectedTlds] = useState<string[]>(['com', 'io', 'co', 'ai']);
  const [filters, setFilters] = useState<Partial<SearchFilters>>({});

  // Initialize state when component mounts
  useEffect(() => {
    console.log('DomainSearchPage mounted');
  }, []);
  const navigate = useNavigate();

  const handleSearchStart = useCallback((searchQuery: string, tlds: string[], filters: Partial<SearchFilters> = {}) => {
    console.log('Search started:', { query: searchQuery, tlds, filters });
    setQuery(searchQuery);
    setIsLoading(true);
    setError(null);
  }, []);

  const handleSearchComplete = useCallback((results: DomainSearchResult[]) => {
    console.log('Search complete:', results);
    setSearchResults(results);
    setIsLoading(false);
  }, []);

  const handleSearchError = useCallback((error: string) => {
    console.error('Search error:', error);
    setError(error);
    setIsLoading(false);
  }, []);

  const handleDomainSelect = useCallback((domain: string) => {
    console.log('Domain selected:', domain);
    // Navigate to domain details or show a modal
  }, [navigate]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Find Your Perfect Domain Name
        </h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <DomainSearch
            onSearchStart={handleSearchStart}
            onSearchComplete={handleSearchComplete}
            onSearchError={handleSearchError}
            className="mb-6"
            initialQuery={query}
            initialTlds={selectedTlds}
            initialFilters={filters}
          />
          
          {isLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
              <p className="mt-2 text-gray-600">Searching for domains...</p>
            </div>
          ) : error ? (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          ) : searchResults.length > 0 ? (
            <div className="mt-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Search Results</h2>
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                  {searchResults.map((result) => (
                    <li key={result.domain}>
                      <div className="px-4 py-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="text-sm font-medium text-blue-600 truncate">
                              {result.domain}
                            </div>
                            {result.is_available ? (
                              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Available
                              </span>
                            ) : (
                              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                Taken
                              </span>
                            )}
                          </div>
                          <div className="ml-2 flex-shrink-0 flex">
                            {result.is_available && (
                              <button
                                type="button"
                                onClick={() => handleDomainSelect(result.domain)}
                                className="mr-3 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                              >
                                Add to Cart
                              </button>
                            )}
                            <button
                              type="button"
                              onClick={() => {}}
                              className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                              Watch
                            </button>
                          </div>
                        </div>
                        {result.price && (
                          <div className="mt-2">
                            <p className="text-sm text-gray-500">
                              ${result.price.toFixed(2)}/year
                            </p>
                          </div>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : query ? (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search or filter to find what you're looking for.
              </p>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Start your domain search
                </h3>
                <div className="mt-2 max-w-xl text-sm text-gray-500">
                  <p>
                    Enter a name or keyword above to check domain availability across multiple TLDs.
                  </p>
                </div>
              </div>
            </div>
          )}
          
          <div className="mt-8 bg-blue-50 border-l-4 border-blue-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h2a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-blue-700">
                  Not finding what you're looking for? Try our advanced name generation tool or contact our support team for assistance.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DomainSearchPage;
