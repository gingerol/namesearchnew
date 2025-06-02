import React, { useState } from 'react';
import { SlidersHorizontal, X, Save } from 'lucide-react';

export interface SearchFilters {
  minPrice: number | '';
  maxPrice: number | '';
  minLength: number | '';
  maxLength: number | '';
  onlyAvailable: boolean;
  onlyPremium: boolean;
  tlds: string[];
  characterTypes: {
    numbers: boolean;
    hyphens: boolean;
    special: boolean;
  };
}

interface AdvancedSearchPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onApplyFilters: (filters: SearchFilters) => void;
  initialFilters?: Partial<SearchFilters>;
  availableTlds?: string[];
}

const defaultFilters: SearchFilters = {
  minPrice: '',
  maxPrice: '',
  minLength: '',
  maxLength: '',
  onlyAvailable: false,
  onlyPremium: false,
  tlds: [],
  characterTypes: {
    numbers: false,
    hyphens: false,
    special: false,
  },
};

export const AdvancedSearchPanel: React.FC<AdvancedSearchPanelProps> = ({
  isOpen,
  onClose,
  onApplyFilters,
  initialFilters = {},
  availableTlds = [],
}) => {
  const [filters, setFilters] = useState<SearchFilters>({
    ...defaultFilters,
    ...initialFilters,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    
    setFilters(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value === '' ? '' : Number(value),
    }));
  };

  const handleCharacterTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    
    setFilters(prev => ({
      ...prev,
      characterTypes: {
        ...prev.characterTypes,
        [name]: checked,
      },
    }));
  };

  const handleTldToggle = (tld: string) => {
    setFilters(prev => ({
      ...prev,
      tlds: prev.tlds.includes(tld)
        ? prev.tlds.filter(t => t !== tld)
        : [...prev.tlds, tld],
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onApplyFilters(filters);
  };

  const handleReset = () => {
    setFilters(defaultFilters);
    onApplyFilters(defaultFilters);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
      
      <div className="absolute inset-y-0 right-0 max-w-full flex">
        <div className="relative w-screen max-w-md">
          <div className="h-full flex flex-col bg-white shadow-xl overflow-y-scroll">
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


              <form onSubmit={handleSubmit} className="mt-6 space-y-6">
                {/* Price Range */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Price Range</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="minPrice" className="block text-sm font-medium text-gray-500 mb-1">
                        Min Price ($)
                      </label>
                      <input
                        type="number"
                        name="minPrice"
                        id="minPrice"
                        min="0"
                        value={filters.minPrice}
                        onChange={handleInputChange}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label htmlFor="maxPrice" className="block text-sm font-medium text-gray-500 mb-1">
                        Max Price ($)
                      </label>
                      <input
                        type="number"
                        name="maxPrice"
                        id="maxPrice"
                        min={filters.minPrice || 0}
                        value={filters.maxPrice}
                        onChange={handleInputChange}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
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
                      />
                    </div>
                  </div>
                </div>


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
                {availableTlds.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">TLD Selection</h3>
                    <div className="flex flex-wrap gap-2">
                      {availableTlds.map(tld => (
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


                <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={handleReset}
                    className="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Reset
                  </button>
                  <button
                    type="submit"
                    className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    <Save className="-ml-1 mr-2 h-4 w-4" />
                    Apply Filters
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
