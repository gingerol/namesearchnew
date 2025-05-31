import React, { useState, useEffect } from 'react';
import { useDebounce } from '../../../hooks/useDebounce';
import { domainSearchApi } from '../api';
import type { DomainSearchResult } from '../types';

interface DomainSearchProps {
  onSearchStart?: () => void;
  onSearchComplete?: (results: DomainSearchResult[]) => void;
  onSearchError?: (error: string) => void;
  className?: string;
}

export const DomainSearch: React.FC<DomainSearchProps> = ({
  onSearchStart,
  onSearchComplete,
  onSearchError,
  className = ''
}) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const debouncedQuery = useDebounce(query, 300);

  // Fetch suggestions when query changes
  useEffect(() => {
    if (debouncedQuery.length > 2) {
      fetchSuggestions(debouncedQuery);
    } else {
      setSuggestions([]);
    }
  }, [debouncedQuery]);

  const fetchSuggestions = async (searchQuery: string) => {
    try {
      const results = await domainSearchApi.getSuggestions(searchQuery, 5);
      setSuggestions(results);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch suggestions';
      setError(errorMessage);
      onSearchError?.(errorMessage);
      console.error('Fetch suggestions error:', err);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    setError(null);
    onSearchStart?.();
    
    try {
      const response = await domainSearchApi.searchDomains({
        query: query.trim(),
        only_available: true,
        limit: 10
      });
      
      onSearchComplete?.(response.results);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to search domains';
      setError(errorMessage);
      onSearchError?.(errorMessage);
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setSuggestions([]);
    // Optionally trigger search immediately when a suggestion is clicked
    // handleSearch(new Event('submit') as unknown as React.FormEvent);
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-2 w-full">
        <div className="relative flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for a domain..."
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={isSearching}
            aria-label="Domain search input"
          />
          
          {/* Suggestions dropdown */}
          {suggestions.length > 0 && (
            <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {suggestions.map((suggestion, index) => (
                <li 
                  key={index}
                  className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-gray-800 hover:text-blue-700"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <button
          type="submit"
          disabled={isSearching || !query.trim()}
          className={`px-6 py-3 text-white font-medium rounded-lg transition-colors ${
            isSearching || !query.trim() 
              ? 'bg-blue-400 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
          aria-label={isSearching ? 'Searching...' : 'Search domains'}
        >
          {isSearching ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Searching...
            </span>
          ) : 'Search'}
        </button>
      </form>
      
      {/* Error message */}
      {error && (
        <div className="p-3 text-sm text-red-700 bg-red-50 rounded-lg">
          {error}
        </div>
      )}
      
      {/* Search tips */}
      <div className="text-sm text-gray-500 mt-2">
        <p>Try searching for a brand name, keyword, or phrase (e.g., "myawesomeapp")</p>
      </div>
    </div>
  );
};
