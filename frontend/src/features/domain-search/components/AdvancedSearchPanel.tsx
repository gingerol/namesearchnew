import React, { useState, useEffect, useCallback } from 'react';
import { useAdvancedSearchStore } from '../advancedSearchStore';
import { X, Save } from 'lucide-react';
import type { SearchFilters, AdvancedDomainSearchRequestFE } from '../types';

// Re-export the SearchFilters interface from types
export type { SearchFilters };

interface AdvancedSearchPanelProps {
  isOpen: boolean;
  onClose: () => void;
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
  availableTlds = [],
}) => {
  // Get store state and actions
  const { 
    currentFilters, 
    setCurrentFilters, 
    fetchAdvancedSearchResults,
    resetSearchState
  } = useAdvancedSearchStore();
  
  // Initialize filters from store and props
  const [filters, setFilters] = useState<SearchFilters>(() => ({
    ...defaultFilters,
    ...initialFilters,
    ...currentFilters,
  }));
  
  // Update local filters when store filters change or panel opens
  useEffect(() => {
    if (isOpen) {
      setFilters(prev => ({
        ...defaultFilters,
        ...initialFilters,
        ...currentFilters,
        // Preserve any local changes that haven't been saved to the store yet
        ...prev
      }));
    }
  }, [isOpen, currentFilters, initialFilters]);
  
  // Handle form reset
  const handleReset = useCallback(() => {
    const resetFilters = {
      ...defaultFilters,
      ...initialFilters,
    };
    setFilters(resetFilters);
    setCurrentFilters(resetFilters);
    resetSearchState();
  }, [initialFilters, resetSearchState, setCurrentFilters]);

  // Use the availableTlds prop with default values
  const tlds = availableTlds.length > 0 ? availableTlds : ['com', 'net', 'org', 'io', 'ai'];
  
  // Update local filters
  const updateFilters = useCallback((updates: Partial<SearchFilters>) => {
    setFilters(prev => ({
      ...prev,
      ...updates,
      // Ensure characterTypes is properly merged
      ...(updates.characterTypes ? {
        characterTypes: {
          ...prev.characterTypes,
          ...updates.characterTypes
        }
      } : {})
    }));
  }, []);
  
  // Update store when filters change
  const updateStoreFilters = useCallback((newFilters: SearchFilters) => {
    setCurrentFilters(newFilters);
  }, [setCurrentFilters]);
  
  // Debounce store updates to prevent excessive renders
  useEffect(() => {
    const timer = setTimeout(() => {
      updateStoreFilters(filters);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [filters, updateStoreFilters]);
  
  // Handle TLD toggle
  const handleTldToggle = useCallback((tld: string) => {
    const newTlds = filters.tlds.includes(tld)
      ? filters.tlds.filter(t => t !== tld)
      : [...filters.tlds, tld];
    updateFilters({ tlds: newTlds });
  }, [filters.tlds, updateFilters]);
  
  // Handle input changes
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    updateFilters({ [name]: type === 'checkbox' ? checked : value });
  }, [updateFilters]);
  
  // Handle text input changes
  const handleTextInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    updateFilters({ [name]: value });
  }, [updateFilters]);
  
  // Handle select changes
  const handleSelectChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    updateFilters({ [name]: value });
  }, [updateFilters]);
  
  // Handle character type changes
  const handleCharacterTypeChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    updateFilters({
      characterTypes: {
        ...filters.characterTypes,
        [name]: checked,
      },
    });
  }, [filters.characterTypes, updateFilters]);
  
  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Prepare search filters with proper typing
      const searchFilters: AdvancedDomainSearchRequestFE = {
        // Include a default query parameter to satisfy backend requirements
        query: 'search', // Default query when none provided
        // Convert filters to match AdvancedDomainSearchRequestFE type
        ...Object.fromEntries(
          Object.entries(filters).map(([key, value]) => {
            // Map SearchFilters properties to AdvancedDomainSearchRequestFE properties
            const mappedKey = key === 'startsWith' ? 'starts_with' :
                             key === 'endsWith' ? 'ends_with' :
                             key === 'minPrice' ? 'min_price' :
                             key === 'maxPrice' ? 'max_price' :
                             key === 'minLength' ? 'min_length' :
                             key === 'maxLength' ? 'max_length' :
                             key === 'onlyAvailable' ? 'only_available' :
                             key === 'onlyPremium' ? 'only_premium' :
                             key === 'minQualityScore' ? 'min_quality_score' :
                             key === 'minSeoScore' ? 'min_seo_score' :
                             key === 'registeredAfter' ? 'registered_after' :
                             key === 'registeredBefore' ? 'registered_before' :
                             key === 'minAgeYears' ? 'min_age_years' :
                             key === 'maxAgeYears' ? 'max_age_years' :
                             key === 'minSearchVolume' ? 'min_search_volume' :
                             key === 'minCpc' ? 'min_cpc' :
                             key === 'sortBy' ? 'sort_by' :
                             key === 'sortOrder' ? 'sort_order' :
                             key;
            
            // Skip undefined, null, or empty string values
            if (value === undefined || value === null || value === '') {
              return [mappedKey, undefined];
            }
            
            // Handle nested characterTypes object
            if (key === 'characterTypes' && typeof value === 'object') {
              return [
                'allow_numbers',
                (value as any).numbers
              ];
            }
            
            return [mappedKey, value];
          })
        )
      };
      
      // Update store with current filters
      setCurrentFilters(filters);
      
      // Perform the search with properly typed filters
      await fetchAdvancedSearchResults(searchFilters);
      onClose();
    } catch (err) {
      console.error('Error performing search:', err);
      // Don't close on error to allow user to see and fix issues
    }
  }, [filters, onClose, setCurrentFilters, fetchAdvancedSearchResults]);

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
      onClick={onClose}
    >
      <div className="absolute inset-0 overflow-hidden">
        <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full">
          <div 
            className="pointer-events-auto w-screen max-w-md transform transition-transform duration-300 ease-in-out"
            style={{
              transform: isOpen ? 'translateX(0)' : 'translateX(100%)'
            }}
            onClick={(e) => e.stopPropagation()}
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
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
