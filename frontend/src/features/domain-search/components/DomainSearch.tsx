import { Search as SearchIcon, X } from 'lucide-react';
import { useCallback, useEffect, useState, useRef } from 'react';
import { AdvancedSearchPanel } from './AdvancedSearchPanel';
import { domainSearchApi } from '../api';
import type { 
  DomainSearchResult, 
  WhoisData,
  SearchFilters
} from '../types';

// Popular TLDs to offer in the quick selector
const POPULAR_TLDS = [
  'com', 'net', 'org', 'io', 'co', 'ai', 'app', 'dev',
  'me', 'us', 'ca', 'uk', 'de', 'in', 'xyz', 'tech', 'ng'
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
  // Component state
  const [isWhois, setIsWhois] = useState(false);
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isWhoisSearching, setIsWhoisSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState(initialQuery);
  const [selectedTlds, setSelectedTlds] = useState<string[]>(initialTlds);
  const [activeFilters, setActiveFilters] = useState<Partial<SearchFilters>>(initialFilters);
  const panelRef = useRef<HTMLDivElement>(null);

  // Initialize state from props once when component mounts
  useEffect(() => {
    // Only update if the props have changed
    if (initialQuery && initialQuery !== query) {
      console.log('Updating query from props:', initialQuery);
      setQuery(initialQuery);
    }
    
    // Only update TLDs if they've changed and we're not already in the middle of a state update
    if (initialTlds && JSON.stringify(initialTlds) !== JSON.stringify(selectedTlds)) {
      console.log('Updating TLDs from props:', initialTlds);
      setSelectedTlds(initialTlds);
    }
  }, [initialQuery, initialTlds]);

  // Escape key handling
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isSearching) {
        setIsSearching(false);
        setError('Search cancelled');
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isSearching]);

  // Debug logging - only in development
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('AdvancedSearchPanel isOpen:', isAdvancedOpen);
      console.log('Active filters:', activeFilters);
    }
  }, [isAdvancedOpen, activeFilters]);

  // Close panel when clicking outside
  useEffect(() => {
    if (!isAdvancedOpen) return;
    
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsAdvancedOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isAdvancedOpen]);

  // Handle search
  // Helper function to adapt WhoisData to DomainSearchResult format
  const adaptWhoisToDomainResult = (whoisData: WhoisData): DomainSearchResult => {
    try {
      // Handle case where whoisData is null or undefined
      if (!whoisData) {
        console.error('No WHOIS data received');
        throw new Error('No WHOIS data available');
      }

      // Handle error case from backend
      if ('error' in whoisData && whoisData.error) {
        console.error('Error in WHOIS response:', whoisData.error);
        throw new Error(whoisData.error);
      }

      // Ensure we have a valid domain
      const domain = whoisData.domain || '';
      if (!domain) {
        console.error('No domain in WHOIS response:', whoisData);
        throw new Error('Invalid domain in WHOIS response');
      }

      // Extract domain and TLD
      const domainParts = domain.split('.');
      const tld = domainParts.length > 1 ? domainParts[domainParts.length - 1] : '';
      const domainName = domainParts[0] || '';
      
      // Calculate word count from domain name (split by hyphens and underscores)
      const wordCount = domainName ? domainName.split(/[-_]/).filter(Boolean).length : 1;
      
      return {
        domain: domain,
        tld: tld,
        is_available: whoisData.available || false,
        is_premium: whoisData.is_premium || false,
        price: whoisData.price,
        whois_data: whoisData, // Include full WHOIS data for reference
        analysis: {
          linguistic: {
            score: 0, // Default score, can be enhanced with domain analysis
            is_pronounceable: true, // Default assumption
            syllable_count: 0, // Could be calculated if needed
            word_count: wordCount
          },
          brand_archetype: 'generic',
          brand_confidence: 0, // Default confidence
          trademark_risk: 'low' as const
        }
      };
    } catch (error) {
      console.error('Error adapting WHOIS data:', error);
      // Return a fallback result that won't break the UI
      const errorMessage = error instanceof Error ? error.message : 'Unknown error processing WHOIS data';
      return {
        domain: 'error',
        tld: 'com',
        is_available: false,
        is_premium: false,
        error: errorMessage,
        analysis: {
          linguistic: {
            score: 0,
            is_pronounceable: false,
            syllable_count: 0,
            word_count: 0
          },
          brand_archetype: 'unknown',
          brand_confidence: 0,
          trademark_risk: 'low' as const
        }
      };
    }
  };
  
  // Helper function to adapt FilteredDomainInfoFE to DomainSearchResult format
  const adaptFilteredToDomainResult = (domainInfo: any): DomainSearchResult => {
    console.log('Adapting domain info:', domainInfo);
    
    // Handle the new API format where domain and tld are separate properties
    if (domainInfo.domain && domainInfo.tld) {
      return {
        domain: domainInfo.domain,
        tld: domainInfo.tld,
        is_available: domainInfo.is_available || false,
        is_premium: domainInfo.is_premium || false,
        price: domainInfo.price,
        analysis: {
          linguistic: {
            score: domainInfo.quality_score || 0,
            is_pronounceable: true,
            syllable_count: 0,
            word_count: 1
          },
          brand_archetype: 'generic',
          brand_confidence: domainInfo.seo_score || 0,
          trademark_risk: 'low' as const
        }
      };
    }
    
    // Fallback to legacy format handling
    const domainName = domainInfo.domain_name_full || 
                     (domainInfo.name_part && domainInfo.tld_part 
                      ? `${domainInfo.name_part}.${domainInfo.tld_part}` 
                      : '');
    
    // Ensure we have a valid domain format
    if (!domainName || !domainName.includes('.')) {
      console.warn('Invalid domain format in response:', domainInfo);
      // Return a fallback that won't break the UI
      return {
        domain: 'invalid-domain',
        tld: 'com',
        is_available: false,
        is_premium: false,
        analysis: {
          linguistic: {
            score: 0,
            is_pronounceable: false,
            syllable_count: 0,
            word_count: 0
          },
          brand_archetype: 'unknown',
          brand_confidence: 0,
          trademark_risk: 'low' as const
        }
      };
    }
    
    // Extract the domain and TLD parts
    const domainParts = domainName.split('.');
    const domain = domainParts[0];
    const tld = domainParts.slice(1).join('.');
    
    return {
      domain: domain,
      tld: tld || 'com',
      is_available: domainInfo.is_available || false,
      is_premium: domainInfo.is_premium || false,
      price: domainInfo.price,
      analysis: {
        linguistic: {
          score: domainInfo.quality_score || 0,
          is_pronounceable: true,
          syllable_count: 0,
          word_count: 1
        },
        brand_archetype: 'generic',
        brand_confidence: domainInfo.seo_score || 0,
        trademark_risk: 'low' as const
      }
    };
  };

  const handleSearch = useCallback(async () => {
    if (!query) return;
    
    console.log('Initiating search with query:', query, 'and TLDs:', selectedTlds, 'isWhois:', isWhois);
    
    try {
      if (isWhois) {
        // WHOIS search
        setIsWhoisSearching(true);
        setError(null);
        onSearchStart(query, selectedTlds, activeFilters);
        
        console.log('Initiating WHOIS search for:', query);
        let domainToCheck = query;
        if (selectedTlds.length > 0) {
          const selectedTld = selectedTlds[0].replace(/^\./, ''); // remove leading dot if present
          // Only append if not already ending with the selected TLD
          if (!domainToCheck.toLowerCase().endsWith(`.${selectedTld.toLowerCase()}`)) {
            domainToCheck = `${domainToCheck}.${selectedTld}`;
          }
        } else if (!domainToCheck.includes('.')) {
          domainToCheck = `${domainToCheck}.com`;
        }
        
        console.log('Sending WHOIS request for domain:', domainToCheck);
        
        try {
          const response = await domainSearchApi.whois(domainToCheck);
          console.log('WHOIS response received:', response);
          
          if (!response) {
            throw new Error('Empty WHOIS response received');
          }
          
          // Adapt WHOIS data to DomainSearchResult format
          const adaptedResult = adaptWhoisToDomainResult(response);
          console.log('Adapted WHOIS result:', adaptedResult);
          
          if (adaptedResult.error) {
            throw new Error(adaptedResult.error);
          }
          
          onSearchComplete([adaptedResult]);
        } catch (error) {
          console.error('Error in WHOIS search:', error);
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch WHOIS data';
          setError(errorMessage);
          onSearchError(errorMessage);
          // Still call onSearchComplete with an empty array to reset any loading states
          onSearchComplete([]);
        } finally {
          setIsWhoisSearching(false);
        }
      } else {
        // Domain search
        setIsSearching(true);
        setError(null);
        onSearchStart(query, selectedTlds, activeFilters);
        
        // Prepare search parameters
        const searchParams: any = {};
        
        // Only include query if it's not empty
        if (query) {
          searchParams.query = query;
        }
        
        // Always include TLDs, fallback to common ones if none selected
        searchParams.tlds = selectedTlds.length > 0 ? selectedTlds : ['com', 'io', 'ai'];
        
        // Include any advanced filters
        Object.assign(searchParams, activeFilters);
        
        console.log('Sending search request with params:', searchParams);
        
        const response = await domainSearchApi.searchDomains(searchParams);
        console.log('Search response received:', response);
        
        if (!response || !Array.isArray(response.results)) {
          throw new Error('Invalid search response format');
        }
        
        // Adapt filtered domain info to DomainSearchResult format
        const adaptedResults = response.results.map(adaptFilteredToDomainResult);
        console.log('Adapted search results:', adaptedResults);
        
        if (adaptedResults.length === 0) {
          console.log('No results found for search');
        }
        
        onSearchComplete(adaptedResults);
      }
    } catch (err) {
      console.error('Search error:', err);
      const errorMessage = err instanceof Error ? err.message : 
                          typeof err === 'string' ? err : 'An unknown error occurred';
      console.error('Error details:', { error: err });
      setError(errorMessage);
      onSearchError(errorMessage);
    } finally {
      setIsWhoisSearching(false);
      setIsSearching(false);
    }
  }, [query, selectedTlds, activeFilters, onSearchStart, onSearchComplete, onSearchError, isWhois]);

  // Toggle WHOIS mode
  const toggleWhois = useCallback(() => {
    setIsWhois(prev => !prev);
  }, []);

  // Handle TLD selection
  const toggleTld = useCallback((tld: string) => {
    setSelectedTlds(prev => 
      prev.includes(tld) 
        ? prev.filter(t => t !== tld)
        : [...prev, tld]
    );
  }, []);

  // Handle TLD select all
  const handleTldSelectAll = useCallback(() => {
    setSelectedTlds(POPULAR_TLDS);
  }, []);

  // Handle TLD clear
  const handleTldClear = useCallback(() => {
    setSelectedTlds([]);
  }, []);

  // Handle advanced filters toggle
  const toggleAdvanced = useCallback(() => {
    setIsAdvancedOpen(prev => !prev);
  }, []);

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your business name or keywords..."
            className={`w-full pl-10 pr-4 py-3 text-base border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              error ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={isSearching}
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={toggleWhois}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 flex items-center gap-1"
          >
            <span className="hidden sm:inline">WHOIS</span>
          </button>

          <button
            type="button"
            onClick={toggleAdvanced}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 flex items-center gap-1"
          >
            <SearchIcon className="w-4 h-4" />
            <span className="hidden sm:inline">Advanced</span>
          </button>

          <button
            type="button"
            onClick={handleSearch}
            disabled={isSearching || !query}
            className={`px-6 py-2 rounded-lg ${isSearching ? 'bg-gray-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
          >
            {isSearching ? (
              <>
                <div className="w-5 h-5 border-2 border-t-transparent border-blue-500 rounded-full animate-spin" /> 
                {isWhois ? 'Checking WHOIS...' : 'Searching...'}
              </>
            ) : (
              isWhois ? 'Check WHOIS' : 'Search'
            )}
          </button>
        </div>
      </div>

      <div className="flex justify-between items-center mb-2">
        <h3 className="text-sm font-medium text-gray-700">Domain Extensions</h3>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleTldSelectAll}
            className="text-xs text-blue-600 hover:underline"
          >
            Select All
          </button>
          <span className="text-gray-300">|</span>
          <button
            type="button"
            onClick={handleTldClear}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {POPULAR_TLDS.map((tld) => {
          const isSelected = selectedTlds.includes(tld);
          return (
            <button
              key={tld}
              type="button"
              onClick={() => toggleTld(tld)}
              className={`px-3 py-1 text-sm rounded-full transition-colors cursor-pointer ${
                isSelected
                  ? 'bg-blue-600 text-white border border-blue-600 font-medium'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
              aria-pressed={isSelected}
              aria-label={`Toggle ${tld} domain extension`}
            >
              .{tld}
            </button>
          );
        })}
      </div>

      {isAdvancedOpen && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium">Advanced Filters</h3>
            <button
              type="button"
              onClick={toggleAdvanced}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <AdvancedSearchPanel
            isOpen={isAdvancedOpen}
            onClose={() => {
              toggleAdvanced();
              // Manually update active filters when the panel is closed
              // This is a workaround since we removed the onApplyFilters prop
              setActiveFilters(current => ({ ...current }));
            }}
            initialFilters={activeFilters}
            availableTlds={POPULAR_TLDS}
          />
        </div>
      )}

      {(isSearching || isWhoisSearching) && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-lg">
            <div className="flex flex-col items-center gap-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              <p className="text-lg font-semibold">{isWhois ? 'Checking WHOIS...' : 'Searching Domains...'}</p>
              <p className="text-gray-600">Please wait while we {isWhois ? 'check WHOIS data' : 'find the perfect domain for you'}</p>
              <button 
                type="button" 
                onClick={() => {
                  // Set loading states to false first to prevent race conditions
                  if (isWhois) {
                    setIsWhoisSearching(false);
                  } else {
                    setIsSearching(false);
                  }
                  // Notify parent component about the cancellation
                  onSearchError('Search was cancelled');
                  setError('Search was cancelled');
                }} 
                className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                disabled={!isSearching && !isWhoisSearching}
              >
                Cancel Search
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
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
      )}
    </div>
  );
};
