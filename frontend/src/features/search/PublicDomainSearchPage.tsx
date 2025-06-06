import React, { useCallback, useState } from 'react';
import { DomainSearch } from '../domain-search/components/DomainSearch';
import { DomainResults } from '../domain-search/components/DomainResults';
import type { DomainSearchResult, SearchFilters } from '../domain-search/types';

export const PublicDomainSearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [selectedTlds] = useState<string[]>(['com', 'io', 'co', 'ai']);
  const [filters] = useState<Partial<SearchFilters>>({});
  const [searchResults, setSearchResults] = useState<DomainSearchResult[]>([]);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearchStart = useCallback((searchQuery: string, tlds: string[], searchFilters: Partial<SearchFilters> = {}) => {
    console.log('Public search started:', { query: searchQuery, tlds, filters: searchFilters });
    setQuery(searchQuery);
    setSearchError(null);
    setHasSearched(false);
  }, []);

  const handleSearchComplete = useCallback((results: DomainSearchResult[]) => {
    console.log('Public search complete:', results);
    setSearchResults(results);
    setHasSearched(true);
  }, []);

  const handleSearchError = useCallback((error: string) => {
    console.error('Public search error:', error);
    setSearchError(error);
    setHasSearched(true);
  }, []);

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
            initialQuery={query}
            initialTlds={selectedTlds}
            initialFilters={filters}
          />
        </div>

        {hasSearched && (
          <div className="mt-8">
            {searchError ? (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700">{searchError}</p>
              </div>
            ) : searchResults.length === 0 ? (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-700">No domains found matching your search criteria.</p>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <DomainResults 
                  results={searchResults} 
                  onSelect={(domain: string) => {
                    // Handle domain selection (e.g., navigate to domain details)
                    console.log('Selected domain:', domain);
                  }}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PublicDomainSearchPage;
