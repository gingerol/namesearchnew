import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { domainSearchApi } from './api'; // Adjusted path: from ../api to ./api
import type {
  AdvancedDomainSearchRequestFE,
  FilteredDomainInfoFE,
  PaginatedFilteredDomainsResponseFE,
} from './types'; // Adjusted path: from ../types to ./types

interface AdvancedSearchState {
  results: FilteredDomainInfoFE[];
  totalItems: number;
  currentPage: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  currentFilters: AdvancedDomainSearchRequestFE;
  // Actions
  setLoading: (isLoading: boolean) => void;
  setSearchResults: (response: PaginatedFilteredDomainsResponseFE) => void;
  setSearchError: (error: string | null) => void;
  setCurrentFilters: (filters: Partial<AdvancedDomainSearchRequestFE>) => void;
  setCurrentPage: (page: number) => void;
  setPageSize: (size: number) => void;
  fetchAdvancedSearchResults: (requestFilters?: Partial<AdvancedDomainSearchRequestFE>) => Promise<PaginatedFilteredDomainsResponseFE | undefined>;
  resetSearchState: () => void;
}

const initialAdvancedSearchState: Omit<AdvancedSearchState, 'setLoading' | 'setSearchResults' | 'setSearchError' | 'setCurrentFilters' | 'setCurrentPage' | 'setPageSize' | 'fetchAdvancedSearchResults' | 'resetSearchState'> = {
  results: [],
  totalItems: 0,
  currentPage: 1,
  pageSize: 20, // Default page size
  totalPages: 0,
  isLoading: false,
  error: null,
  currentFilters: { page: 1, page_size: 20 }, // Initial filters with pagination
};

export const useAdvancedSearchStore = create<AdvancedSearchState>()(
  devtools(
    (set, get) => ({
      ...initialAdvancedSearchState,

      setLoading: (isLoading) => set({ isLoading, error: null }), // Clear error when loading starts

      setSearchResults: (response) =>
        set({
          results: response.results,
          totalItems: response.total_items,
          currentPage: response.page,
          pageSize: response.page_size,
          totalPages: response.total_pages,
          isLoading: false,
          error: null,
        }),

      setSearchError: (error) => set({ error, isLoading: false, results: [], totalItems: 0, totalPages: 0 }),

      setCurrentFilters: (filters) =>
        set((state) => ({
          currentFilters: { ...state.currentFilters, ...filters },
          // Reset page to 1 when filters change, unless page is explicitly being set by the filter update
          currentPage: filters.page !== undefined ? filters.page : (state.currentFilters.page !== 1 ? 1 : state.currentPage) 
        })),
      
      setCurrentPage: (page) => set({ currentPage: page }),

      setPageSize: (size) => set({ pageSize: size, currentPage: 1 }), // Reset to page 1 on page size change

      fetchAdvancedSearchResults: async (requestFilters?: Partial<AdvancedDomainSearchRequestFE>) => {
        const store = get();
        let effectiveFilters = { ...store.currentFilters };

        if (requestFilters && Object.keys(requestFilters).length > 0) {
          // If new filters are passed, update currentFilters in the store
          store.setCurrentFilters(requestFilters);
          // Use the updated filters from the store for the current fetch
          effectiveFilters = { ...get().currentFilters };
        }
        
        // Handle both query and keywords for backward compatibility
        const query = requestFilters?.query || 
                    (requestFilters?.keywords ? requestFilters.keywords[0] : '') || 
                    effectiveFilters.query || 
                    '';
        
        // Construct final payload with proper typing
        const finalPayload: AdvancedDomainSearchRequestFE = {
          ...effectiveFilters,
          ...requestFilters,
          query, // Always include query
          // Remove empty arrays and undefined values
          ...(effectiveFilters.tlds?.length ? { tlds: effectiveFilters.tlds } : { tlds: ['com', 'io', 'co', 'ai'] }),
          page: requestFilters?.page !== undefined ? requestFilters.page : store.currentPage,
          page_size: requestFilters?.page_size !== undefined ? requestFilters.page_size : store.pageSize,
        };

        // Clean up undefined values and ensure required fields
        const cleanPayload: AdvancedDomainSearchRequestFE & { query: string } = {
          ...Object.fromEntries(
            Object.entries(finalPayload).filter(([_, v]) => v !== undefined && v !== '')
          ),
          query // Ensure query is always included
        };

        store.setLoading(true);
        try {
          const response = await domainSearchApi.searchDomains(cleanPayload);
          store.setSearchResults(response);
          return response; // Return the response for component-level handling
        } catch (err: any) {
          store.setSearchError(err.message || 'An unknown error occurred');
          throw err; // Re-throw to allow component to handle the error
        }
      },
      
      resetSearchState: () => set(initialAdvancedSearchState),
    }),
    { name: 'AdvancedSearchStore' }
  )
);
