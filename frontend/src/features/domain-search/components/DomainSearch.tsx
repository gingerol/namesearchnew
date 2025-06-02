import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useDebounce } from '../../../hooks/useDebounce';
import { domainSearchApi } from '../api';
import type { DomainSearchResult, DomainAnalysis, SearchFilters } from '../types';
import { Search, Loader2, SlidersHorizontal } from 'lucide-react';
import { AdvancedSearchPanel } from './AdvancedSearchPanel';

const POPULAR_TLDS = [
  'com', 'net', 'org', 'io', 'co', 'ai', 'app', 'dev',
  'me', 'us', 'ca', 'uk', 'de', 'in', 'xyz', 'tech'
];

interface DomainSearchProps {
  onSearchStart: (query: string, tlds: string[], filters?: Partial<SearchFilters>) => void;
  onSearchComplete: (results: DomainSearchResult[]) => void;
  onSearchError: (error: string) => void;
  className?: string;
  initialQuery?: string;
  initialTlds?: string[];
  initialFilters?: Partial<SearchFilters>;
}

export const DomainSearch: React.FC<DomainSearchProps> = ({
  onSearchStart,
  onSearchComplete,
  onSearchError,
  className = '',
  initialQuery = '',
  initialTlds = ['com', 'io', 'co', 'ai'],
  initialFilters = {}
}) => {
  // Advanced search panel state
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [activeFilters, setActiveFilters] = useState<Partial<SearchFilters>>(initialFilters);
  const panelRef = useRef<HTMLDivElement>(null);
  
  // Close panel when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsAdvancedOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  const [query, setQuery] = useState(initialQuery);
  const [selectedTlds, setSelectedTlds] = useState<string[]>(initialTlds);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const [error, setError] = useState<string | null>(null);
  
  // Update local state when props change
  useEffect(() => {
    if (initialQuery) setQuery(initialQuery);
    if (initialTlds) setSelectedTlds(initialTlds);
  }, [initialQuery, initialTlds]);
  
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

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    const searchQuery = query.trim();
    if (!searchQuery || selectedTlds.length === 0) return;
    
    setIsSearching(true);
    setError(null);
    
    // Apply filters if any are active
    const filtersToApply = Object.keys(activeFilters).length > 0 
      ? { ...activeFilters, tlds: selectedTlds }
      : undefined;
      
    onSearchStart(searchQuery, selectedTlds, filtersToApply);
    
    try {
      // Search for each selected TLD
      const searchPromises = selectedTlds.map(async (tld) => {
        const domain = `${searchQuery}.${tld}`.toLowerCase();
        const isAvailable = await domainSearchApi.checkAvailability(domain);
        
        // Create a basic domain analysis (in a real app, this would come from the API)
        const analysis: DomainAnalysis = {
          linguistic: {
            score: Math.floor(Math.random() * 100) / 10 + 7, // Random score 7-17
            is_pronounceable: true,
            syllable_count: Math.ceil(searchQuery.length / 3),
            word_count: searchQuery.split(/\s+/).filter(Boolean).length || 1,
          },
          brand_archetype: 'Creator',
          brand_confidence: 0.8,
          trademark_risk: 'low' as const,
        };
        
        return {
          domain,
          tld,
          is_available: isAvailable,
          is_premium: false,
          price: isAvailable ? 14.99 : undefined,
          analysis,
        } as DomainSearchResult;
      });
      
      const results = await Promise.all(searchPromises);
      onSearchComplete(results);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to search domains';
      setError(errorMessage);
      onSearchError(errorMessage);
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  }, [query, selectedTlds, onSearchStart, onSearchComplete, onSearchError]);

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setSuggestions([]);
    // Optionally trigger search immediately when a suggestion is clicked
    // handleSearch(new Event('submit') as unknown as React.FormEvent);
  };

  const toggleTld = (tld: string) => {
    setSelectedTlds(prev => 
      prev.includes(tld) 
        ? prev.filter(t => t !== tld)
        : [...prev, tld]
    );
  };

  const handleTldSelectAll = () => {
    setSelectedTlds(POPULAR_TLDS);
  };

  const handleTldClear = () => {
    setSelectedTlds([]);
  };

  // Handle applying filters from the advanced panel
  const handleApplyFilters = useCallback((filters: SearchFilters) => {
    setActiveFilters(filters);
    setIsAdvancedOpen(false);
    
    // Trigger a new search with the updated filters
    if (query.trim()) {
      onSearchStart(query, selectedTlds, filters);
    }
  }, [query, selectedTlds, onSearchStart]);

  // Count active filters
  const activeFilterCount = Object.values(activeFilters).filter(
    (value) => 
      (typeof value === 'boolean' && value) ||
      (Array.isArray(value) && value.length > 0) ||
      (value !== '' && value !== undefined && value !== null)
  ).length;

  return (
    <div className={`space-y-4 ${className}`}>
      <form onSubmit={handleSearch} className="space-y-3">
        <div className="flex flex-col sm:flex-row gap-2 w-full">
          <div className="relative flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter a name or keyword..."
                className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  error ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isSearching}
                aria-label="Domain search input"
              />
            </div>
          {/* Suggestions dropdown */}
          {suggestions.length > 0 && (
            <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {suggestions.map((suggestion, index) => (
                <li 
                  key={index}
                  className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-gray-800 hover:text-blue-700 flex items-center"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  <span className="font-medium">{suggestion}</span>
                  <span className="ml-2 text-sm text-gray-500">.com .io .ai</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        {/* Search button */}
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setIsAdvancedOpen(true)}
            className={`inline-flex items-center px-4 py-3 border rounded-lg font-medium ${
              activeFilterCount > 0
                ? 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
            aria-label="Advanced search filters"
          >
            <SlidersHorizontal className="h-5 w-5 mr-2" />
            {activeFilterCount > 0 && (
              <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-blue-800 bg-blue-100 rounded-full ml-1">
                {activeFilterCount}
              </span>
            )}
          </button>
          <button
            type="submit"
            disabled={isSearching || !query.trim() || selectedTlds.length === 0}
            className={`px-6 py-3 text-white font-medium rounded-lg transition-colors whitespace-nowrap ${
              isSearching || !query.trim() || selectedTlds.length === 0
                ? 'bg-blue-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
            aria-label={isSearching ? 'Searching...' : 'Search domains'}
          >
            {isSearching ? (
              <span className="flex items-center justify-center">
                <Loader2 className="animate-spin mr-2 h-4 w-4" />
                Searching...
              </span>
            ) : (
              <span className="flex items-center">
                <Search className="mr-2 h-4 w-4" />
                Search
              </span>
            )}
          </button>
        </div>
      </div>
      {/* Selected TLDs */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-gray-500">Extensions:</span>
        {POPULAR_TLDS.map((tld) => (
          <button
            key={tld}
            type="button"
            onClick={() => toggleTld(tld)}
            className={`px-3 py-1 text-sm rounded-full transition-colors ${
              selectedTlds.includes(tld)
                ? 'bg-blue-100 text-blue-800 border border-blue-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            .{tld}
          </button>
        ))}
        <button
          type="button"
          onClick={handleTldSelectAll}
          className="text-sm text-blue-600 hover:underline"
        >
          Select All
        </button>
        <button
          type="button"
          onClick={handleTldClear}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Clear
        </button>
      </div>
      {/* Active filters */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span className="text-gray-500">Active filters:</span>
          {activeFilters.minPrice && (
            <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs">
              Min: ${activeFilters.minPrice}
            </span>
          )}
          {activeFilters.maxPrice && (
            <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs">
              Max: ${activeFilters.maxPrice}
            </span>
          )}
          {activeFilters.onlyAvailable && (
            <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs">
              Available Only
            </span>
          )}
          {activeFilters.onlyPremium && (
            <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs">
              Premium Only
            </span>
          )}
          <button
            type="button"
            onClick={() => setActiveFilters({})}
            className="ml-2 text-sm text-red-600 hover:underline"
          >
            Clear all
          </button>
        </div>
      )}
      {/* Error message */}
      {error && (
        <div className="p-3 text-sm text-red-700 bg-red-50 rounded-lg">
          {error}
        </div>
      )}
    </form>
    {/* Search tips */}
    <div className="text-sm text-gray-500 mt-2">
      <p>Tip: Try searching for a brand name, keyword, or phrase (e.g., "myawesomeapp")</p>
    </div>
    {/* Advanced Search Panel */}
    <div ref={panelRef}>
      <AdvancedSearchPanel
        isOpen={isAdvancedOpen}
        onClose={() => setIsAdvancedOpen(false)}
        onApplyFilters={handleApplyFilters}
        initialFilters={activeFilters}
        availableTlds={POPULAR_TLDS}
      />
    </div>
  </div>
);
};
