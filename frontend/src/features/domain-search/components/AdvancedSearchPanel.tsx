import React, { useState, useEffect, useCallback } from 'react';
import { useAdvancedSearchStore } from '../advancedSearchStore';
import { X, Save } from 'lucide-react';
import type { SearchFilters, AdvancedDomainSearchRequestFE, FilteredDomainInfoFE } from '../types';
// Removed PaginatedFilteredDomainsResponseFE and domainSearchApi as they are no longer used directly

// Re-export the SearchFilters interface from types
export type { SearchFilters };

interface AdvancedSearchPanelProps {
  isOpen: boolean;
  onClose: () => void;
  // onApplyFilters: (filters: SearchFilters) => void; // Removed as store handles filter application
  initialFilters?: Partial<SearchFilters>;
  availableTlds?: string[];
}

const defaultFilters: SearchFilters = {
  // Price filters
  minPrice: '',
  maxPrice: '',
  
  // Length filters
  minLength: '',
  maxLength: '',
  
  // Availability
  onlyAvailable: false,
  onlyPremium: false,
  
  // Domain characteristics
  tlds: [],
  startsWith: '',
  endsWith: '',
  contains: '',
  exclude: '',
  
  // Character types
  characterTypes: {
    numbers: false,
    hyphens: false,
    special: false,
    letters: false,
  },
  
  // Domain quality
  minQualityScore: undefined,
  minSeoScore: undefined,
  
  // Registration date
  registeredAfter: '',
  registeredBefore: '',
  
  // Domain age
  minAgeYears: undefined,
  maxAgeYears: undefined,
  
  // Popularity
  minSearchVolume: undefined,
  minCpc: undefined,
  
  // Language
  language: '',
  
  // Sorting
  sortBy: 'relevance',
  sortOrder: 'desc',
};

export const AdvancedSearchPanel: React.FC<AdvancedSearchPanelProps> = ({
  isOpen,
  onClose,
  initialFilters = {},
  availableTlds = [], // Add default value for availableTlds
}) => {


  // Local state for form inputs - will be replaced by store in Phase 2
  const [filters, setFilters] = useState<SearchFilters>({
    ...defaultFilters,
    ...initialFilters,
  });
  
  // Use the availableTlds prop with default values
  const tlds = availableTlds.length > 0 ? availableTlds : ['com', 'net', 'org', 'io', 'ai'];
  
  const handleTldToggle = (tld: string) => {
    setFilters(prev => {
      const newTlds = prev.tlds.includes(tld)
        ? prev.tlds.filter(t => t !== tld)
        : [...prev.tlds, tld];
      return {
        ...prev,
        tlds: newTlds
      };
    });
  };

  // Connect to Zustand store
  const {
    isLoading,
    error,
    fetchAdvancedSearchResults,
    // Results and pagination will be consumed from store by a display component later
    // results: storeResults,
    // currentPage: storeCurrentPage,
    // pageSize: storePageSize,
    // totalItems: storeTotalItems,
    // totalPages: storeTotalPages,
  } = useAdvancedSearchStore();

  // Local state for search results and pagination - will be removed once a display component consumes from store
  const [searchResults, setSearchResults] = useState<FilteredDomainInfoFE[]>([]);
  const [paginationInfo, setPaginationInfo] = useState<{
    page: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
  } | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    
    setFilters((prev: SearchFilters) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value === '' ? '' : Number(value),
    }));
  };

  const handleTextInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters((prev: SearchFilters) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev: SearchFilters) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCharacterTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    
    setFilters((prev: SearchFilters) => ({
      ...prev,
      characterTypes: {
        ...prev.characterTypes,
        [name]: checked,
      },
    }));
  };

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    // setLoading(true); // Store action will set loading
    // setError(null); // Store action will clear error
    setSearchResults([]); // Clear local results, will eventually be driven by store
    setPaginationInfo(null); // Clear local pagination, will eventually be driven by store

    // Helper to convert string to number or undefined
    const toNumberOrUndefined = (val: string | number | undefined): number | undefined => {
      if (val === undefined || val === '') return undefined;
      const num = Number(val);
      return isNaN(num) ? undefined : num;
    };

    const apiRequestParams: AdvancedDomainSearchRequestFE = {
      // DEV_NOTE: `filters.contains` is currently used as the primary keyword source for the API.
      // Consider adding a dedicated 'keywords' field to SearchFilters if 'contains' has a different meaning.
      keywords: filters.contains && filters.contains.trim() ? [filters.contains.trim()] : undefined,
      tlds: filters.tlds && filters.tlds.length > 0 ? filters.tlds : undefined,
      min_price: toNumberOrUndefined(filters.minPrice),
      max_price: toNumberOrUndefined(filters.maxPrice),
      min_length: toNumberOrUndefined(filters.minLength),
      max_length: toNumberOrUndefined(filters.maxLength),
      page: 1, // Default to page 1 for new search
      page_size: 20, // Default page size

      // Availability
      only_available: filters.onlyAvailable,
      only_premium: filters.onlyPremium,

      // Domain characteristics
      starts_with: filters.startsWith || undefined,
      ends_with: filters.endsWith || undefined,
      exclude_pattern: filters.exclude || undefined,

      // Character types
      allow_numbers: filters.characterTypes.numbers,
      allow_hyphens: filters.characterTypes.hyphens,
      allow_special_chars: filters.characterTypes.special,
      // Not sending allow_letters, assuming it's default true unless restricted by other flags

      // Domain quality
      min_quality_score: toNumberOrUndefined(filters.minQualityScore),
      min_seo_score: toNumberOrUndefined(filters.minSeoScore),

      // Registration date - ensure proper date format if provided
      registered_after: filters.registeredAfter ? new Date(filters.registeredAfter).toISOString().split('T')[0] : undefined,
      registered_before: filters.registeredBefore ? new Date(filters.registeredBefore).toISOString().split('T')[0] : undefined,

      // Domain age
      min_age_years: toNumberOrUndefined(filters.minAgeYears),
      max_age_years: toNumberOrUndefined(filters.maxAgeYears),

      // Popularity
      min_search_volume: toNumberOrUndefined(filters.minSearchVolume),
      min_cpc: toNumberOrUndefined(filters.minCpc),

      // Language - only include if not empty
      language_codes: filters.language && filters.language.trim() ? [filters.language.trim()] : undefined,

      // Sorting - ensure we have defaults
      sort_by: filters.sortBy || 'relevance',
      sort_order: filters.sortOrder || 'desc',
    };

    try {
      console.log('Submitting search with params:', apiRequestParams);
      
      // Clean up the request parameters
      const cleanParams = Object.fromEntries(
        Object.entries(apiRequestParams).filter(([_, v]) => v !== undefined && v !== '')
      ) as AdvancedDomainSearchRequestFE;
      
      // Execute the search
      const response = await fetchAdvancedSearchResults(cleanParams);
      console.log('Search response:', response);
      
      if (response?.results) {
        // Update local state with results
        setSearchResults(response.results);
        setPaginationInfo({
          page: response.page || 1,
          pageSize: response.page_size || 20,
          totalItems: response.total_items || 0,
          totalPages: response.total_pages || 1
        });
      } else {
        console.warn('No results returned from search');
        setSearchResults([]);
        setPaginationInfo({
          page: 1,
          pageSize: 20,
          totalItems: 0,
          totalPages: 1
        });
      }
    } catch (err: any) {
      console.error('Search error:', err);
      // Set error state
      setSearchResults([]);
      setPaginationInfo(null);
      // You might want to display an error message to the user here
    }
    // isLoading is handled by the store
  }, [fetchAdvancedSearchResults, filters /* filters still a dependency for apiRequestParams */]); // UX Decision: Keep panel open to show results, or close. For now, keeping it open.

  const handleReset = () => {
    setFilters({
      ...defaultFilters,
      ...initialFilters,
    });
  };

  // Effect to handle Escape key press
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  // Handler for clicking on the overlay (backdrop)
  const handleOverlayClick = () => {
    onClose();
  };

  // Handler for clicks within the panel content to prevent closing
  const handlePanelContentClick = (event: React.MouseEvent<HTMLDivElement>) => {
    event.stopPropagation();
  };

  if (!isOpen) return null;

  return (
    <div
      className={`fixed inset-0 overflow-hidden transition-all duration-300 ease-in-out z-[9999] ${
        isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}
      style={{
        backgroundColor: isOpen ? 'rgba(0, 0, 0, 0.5)' : 'transparent',
        transition: 'background-color 300ms ease-in-out'
      }}
      onClick={handleOverlayClick}
    >
      <div className="absolute inset-0 overflow-hidden">
        <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full">
          <div 
            className="pointer-events-auto w-screen max-w-md transform transition-transform duration-300 ease-in-out"
            style={{
              transform: isOpen ? 'translateX(0)' : 'translateX(100%)'
            }}
            onClick={handlePanelContentClick}
          >
            <div className="flex h-full flex-col overflow-y-auto bg-white py-6 shadow-xl" style={{ maxHeight: '100vh' }}>
              <div className="flex-1 overflow-y-auto py-6 px-4 sm:px-6">
                <div className="flex items-start justify-between">
                  <h2 className="text-lg font-medium text-gray-900">Advanced Search</h2>
                  <button
                    type="button"
                    className="text-gray-400 hover:text-gray-500"
                    onClick={onClose}
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>

                {/* API Status Messages */}
                {isLoading && <div className="mt-4 p-3 bg-blue-50 text-blue-700 rounded-md">Loading search results...</div>}
                {error && <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md">Error: {error}</div>}

                {/* Search Form */}
                <form onSubmit={handleSubmit} className="mt-6 space-y-6">
                  {/* Price Range */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Price Range ($)</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="minPrice" className="block text-sm font-medium text-gray-500 mb-1">
                          Min Price
                        </label>
                        <input
                          type="number"
                          name="minPrice"
                          id="minPrice"
                          min="0"
                          step="0.01"
                          value={filters.minPrice}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="0.00"
                        />
                      </div>
                      <div>
                        <label htmlFor="maxPrice" className="block text-sm font-medium text-gray-500 mb-1">
                          Max Price
                        </label>
                        <input
                          type="number"
                          name="maxPrice"
                          id="maxPrice"
                          min={filters.minPrice || 0}
                          step="0.01"
                          value={filters.maxPrice}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="Any"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Domain Length */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Domain Length</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="minLength" className="block text-sm font-medium text-gray-500 mb-1">
                          Min Length
                        </label>
                        <input
                          type="number"
                          name="minLength"
                          id="minLength"
                          min="1"
                          max={filters.maxLength || 63}
                          value={filters.minLength}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="1"
                        />
                      </div>
                      <div>
                        <label htmlFor="maxLength" className="block text-sm font-medium text-gray-500 mb-1">
                          Max Length
                        </label>
                        <input
                          type="number"
                          name="maxLength"
                          id="maxLength"
                          min={filters.minLength || 1}
                          max="63"
                          value={filters.maxLength}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="63"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Domain Characteristics */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Domain Characteristics</h3>
                    <div className="space-y-4">
                      <div>
                        <label htmlFor="contains" className="block text-sm font-medium text-gray-500 mb-1">
                          Must Contain
                        </label>
                        <input
                          type="text"
                          name="contains"
                          id="contains"
                          value={filters.contains}
                          onChange={handleTextInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="e.g., shop, tech"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="startsWith" className="block text-sm font-medium text-gray-500 mb-1">
                            Starts With
                          </label>
                          <input
                            type="text"
                            name="startsWith"
                            id="startsWith"
                            value={filters.startsWith}
                            onChange={handleTextInputChange}
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          />
                        </div>
                        <div>
                          <label htmlFor="endsWith" className="block text-sm font-medium text-gray-500 mb-1">
                            Ends With
                          </label>
                          <input
                            type="text"
                            name="endsWith"
                            id="endsWith"
                            value={filters.endsWith}
                            onChange={handleTextInputChange}
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          />
                        </div>
                      </div>
                      <div>
                        <label htmlFor="exclude" className="block text-sm font-medium text-gray-500 mb-1">
                          Exclude
                        </label>
                        <input
                          type="text"
                          name="exclude"
                          id="exclude"
                          value={filters.exclude}
                          onChange={handleTextInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="e.g., adult, sex"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Character Types */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Character Types</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input
                          id="numbers"
                          name="numbers"
                          type="checkbox"
                          checked={filters.characterTypes.numbers}
                          onChange={handleCharacterTypeChange}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="numbers" className="ml-2 block text-sm text-gray-700">
                          Include numbers
                        </label>
                      </div>
                      <div className="flex items-center">
                        <input
                          id="hyphens"
                          name="hyphens"
                          type="checkbox"
                          checked={filters.characterTypes.hyphens}
                          onChange={handleCharacterTypeChange}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="hyphens" className="ml-2 block text-sm text-gray-700">
                          Include hyphens
                        </label>
                      </div>
                      <div className="flex items-center">
                        <input
                          id="special"
                          name="special"
                          type="checkbox"
                          checked={filters.characterTypes.special}
                          onChange={handleCharacterTypeChange}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="special" className="ml-2 block text-sm text-gray-700">
                          Include special characters
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* TLD Selection */}
                  {tlds.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-3">TLD Selection</h3>
                      <div className="flex flex-wrap gap-2">
                        {tlds.map(tld => (
                          <button
                            key={tld}
                            type="button"
                            onClick={() => handleTldToggle(tld)}
                            className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                              filters.tlds.includes(tld)
                                ? 'bg-blue-100 text-blue-800 border border-blue-300'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                          >
                            .{tld}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Availability */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Availability</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input
                          id="onlyAvailable"
                          name="onlyAvailable"
                          type="checkbox"
                          checked={filters.onlyAvailable}
                          onChange={handleInputChange}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="onlyAvailable" className="ml-2 block text-sm text-gray-700">
                          Show only available domains
                        </label>
                      </div>
                      <div className="flex items-center">
                        <input
                          id="onlyPremium"
                          name="onlyPremium"
                          type="checkbox"
                          checked={filters.onlyPremium}
                          onChange={handleInputChange}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="onlyPremium" className="ml-2 block text-sm text-gray-700">
                          Show only premium domains
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* Domain Quality */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Domain Quality</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="minQualityScore" className="block text-sm font-medium text-gray-500 mb-1">
                          Min Quality Score
                        </label>
                        <input
                          type="number"
                          name="minQualityScore"
                          id="minQualityScore"
                          min="0"
                          max="100"
                          value={filters.minQualityScore || ''}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="0-100"
                        />
                      </div>
                      <div>
                        <label htmlFor="minSeoScore" className="block text-sm font-medium text-gray-500 mb-1">
                          Min SEO Score
                        </label>
                        <input
                          type="number"
                          name="minSeoScore"
                          id="minSeoScore"
                          min="0"
                          max="100"
                          value={filters.minSeoScore || ''}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="0-100"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Registration Date */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Registration Date</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="registeredAfter" className="block text-sm font-medium text-gray-500 mb-1">
                          Registered After
                        </label>
                        <input
                          type="date"
                          name="registeredAfter"
                          id="registeredAfter"
                          value={filters.registeredAfter}
                          onChange={handleTextInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label htmlFor="registeredBefore" className="block text-sm font-medium text-gray-500 mb-1">
                          Registered Before
                        </label>
                        <input
                          type="date"
                          name="registeredBefore"
                          id="registeredBefore"
                          value={filters.registeredBefore}
                          onChange={handleTextInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Domain Age */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Domain Age (Years)</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="minAgeYears" className="block text-sm font-medium text-gray-500 mb-1">
                          Min Age
                        </label>
                        <input
                          type="number"
                          name="minAgeYears"
                          id="minAgeYears"
                          min="0"
                          value={filters.minAgeYears || ''}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="0+"
                        />
                      </div>
                      <div>
                        <label htmlFor="maxAgeYears" className="block text-sm font-medium text-gray-500 mb-1">
                          Max Age
                        </label>
                        <input
                          type="number"
                          name="maxAgeYears"
                          id="maxAgeYears"
                          min={filters.minAgeYears || 0}
                          value={filters.maxAgeYears || ''}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="Any"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Popularity */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Popularity</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="minSearchVolume" className="block text-sm font-medium text-gray-500 mb-1">
                          Min Search Volume
                        </label>
                        <input
                          type="number"
                          name="minSearchVolume"
                          id="minSearchVolume"
                          min="0"
                          value={filters.minSearchVolume || ''}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="0+"
                        />
                      </div>
                      <div>
                        <label htmlFor="minCpc" className="block text-sm font-medium text-gray-500 mb-1">
                          Min CPC ($)
                        </label>
                        <input
                          type="number"
                          name="minCpc"
                          id="minCpc"
                          min="0"
                          step="0.01"
                          value={filters.minCpc || ''}
                          onChange={handleInputChange}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          placeholder="0.00+"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Language */}
                  <div>
                    <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-1">
                      Language
                    </label>
                    <select
                      id="language"
                      name="language"
                      value={filters.language}
                      onChange={handleSelectChange}
                      className="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                    >
                      <option value="">Any language</option>
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                      <option value="de">German</option>
                      <option value="it">Italian</option>
                      <option value="pt">Portuguese</option>
                      <option value="ru">Russian</option>
                      <option value="zh">Chinese</option>
                      <option value="ja">Japanese</option>
                      <option value="ko">Korean</option>
                    </select>
                  </div>

                  {/* Sorting */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Sort Results By</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="sortBy" className="block text-sm font-medium text-gray-500 mb-1">
                          Sort By
                        </label>
                        <select
                          id="sortBy"
                          name="sortBy"
                          value={filters.sortBy}
                          onChange={handleSelectChange}
                          className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                        >
                          <option value="relevance">Relevance</option>
                          <option value="price">Price</option>
                          <option value="length">Length</option>
                          <option value="alphabetical">Alphabetical</option>
                          <option value="popularity">Popularity</option>
                          <option value="age">Age</option>
                          <option value="quality">Quality Score</option>
                          <option value="seo">SEO Score</option>
                        </select>
                      </div>
                      <div>
                        <label htmlFor="sortOrder" className="block text-sm font-medium text-gray-500 mb-1">
                          Order
                        </label>
                        <select
                          id="sortOrder"
                          name="sortOrder"
                          value={filters.sortOrder}
                          onChange={handleSelectChange}
                          className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                        >
                          <option value="asc">Ascending</option>
                          <option value="desc">Descending</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex justify-between pt-6 border-t border-gray-200">
                    <button
                      type="button"
                      onClick={handleReset}
                      className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Reset Filters
                    </button>
                    <div className="flex space-x-3">
                      <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <Save className="-ml-1 mr-2 h-4 w-4" />
                        Apply Filters
                      </button>
                    </div>
                  </div>
                </form>

                {/* Search Results */}
                {searchResults.length > 0 && (
                  <div className="mt-8">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Search Results ({paginationInfo?.totalItems})</h3>
                    <div className="bg-white shadow overflow-hidden sm:rounded-md">
                      <ul role="list" className="divide-y divide-gray-200">
                        {searchResults.map((result, index) => (
                          <li key={`${result.domain_name_full}-${index}`}>
                            <div className="px-4 py-4 sm:px-6">
                              <div className="flex items-center justify-between">
                                <p className="text-sm font-medium text-blue-600 truncate">
                                  {result.domain_name_full}
                                </p>
                                <div className="ml-2 flex-shrink-0 flex">
                                  <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                    {result.is_available ? 'Available' : 'Taken'}
                                  </p>
                                </div>
                              </div>
                              <div className="mt-2 sm:flex sm:justify-between">
                                <div className="sm:flex">
                                  <p className="flex items-center text-sm text-gray-500">
                                    <span className="mr-2">Length: {result.name_part_length}</span>
                                    <span className="mr-2">•</span>
                                    <span>Quality: {result.quality_score}/10</span>
                                  </p>
                                </div>
                                <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                                  {result.price && (
                                    <p className="text-sm font-medium text-gray-900">
                                      ${result.price.toFixed(2)}
                                      <span className="text-gray-500 font-normal">/year</span>
                                    </p>
                                  )}
                                </div>
                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Pagination */}
                    {paginationInfo && paginationInfo.totalPages > 1 && (
                      <nav className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6" aria-label="Pagination">
                        <div className="hidden sm:block">
                          <p className="text-sm text-gray-700">
                            Showing page <span className="font-medium">{paginationInfo.page}</span> of{' '}
                            <span className="font-medium">{paginationInfo.totalPages}</span>
                          </p>
                        </div>
                        <div className="flex-1 flex justify-between sm:justify-end space-x-3">
                          <button
                            type="button"
                            disabled={paginationInfo.page <= 1}
                            onClick={() => {
                              const prevPage = paginationInfo.page - 1;
                              setFilters(prev => ({
                                ...prev,
                                page: prevPage,
                              }));
                            }}
                            className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                              paginationInfo.page <= 1
                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                            }`}
                          >
                            Previous
                          </button>
                          <button
                            type="button"
                            disabled={paginationInfo.page >= paginationInfo.totalPages}
                            onClick={() => {
                              const nextPage = paginationInfo.page + 1;
                              setFilters(prev => ({
                                ...prev,
                                page: nextPage,
                              }));
                            }}
                            className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                              paginationInfo.page >= paginationInfo.totalPages
                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                            }`}
                          >
                            Next
                          </button>
                        </div>
                      </nav>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
