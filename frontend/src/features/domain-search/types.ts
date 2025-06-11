// Domain search related types

export interface WhoisData {
  domain: string;
  available: boolean;
  registered: boolean;
  created_date?: string;
  updated_date?: string;
  expiry_date?: string;
  registrar?: string;
  registrant_name?: string;
  registrant_organization?: string;
  registrant_email?: string;
  name_servers: string[];
  status: string[];
  raw_data?: string;
  last_checked: string;
  is_premium?: boolean;
  price?: number;
  error?: string;
}

export interface DomainAnalysis {
  linguistic: {
    score: number;
    is_pronounceable: boolean;
    syllable_count: number;
    word_count: number;
  };
  brand_archetype: string;
  brand_confidence: number;
  trademark_risk: 'low' | 'medium' | 'high';
}

export interface DomainSearchResult {
  domain: string;
  tld: string;
  is_available: boolean;
  is_premium: boolean;
  price?: number;
  whois_data?: WhoisData;
  error?: string;
  analysis: DomainAnalysis;
}

export interface DomainSearchResponse {
  results: DomainSearchResult[];
  total: number;
  available: number;
  taken: number;
  premium: number;
  query: string;
}

export interface SearchFilters {
  // Price filters
  minPrice?: number | '';
  maxPrice?: number | '';
  
  // Length filters
  minLength?: number | '';
  maxLength?: number | '';
  
  // Availability
  onlyAvailable: boolean;
  onlyPremium: boolean;
  
  // Domain characteristics
  tlds: string[];
  startsWith?: string;
  endsWith?: string;
  contains?: string;
  exclude?: string;
  
  // Character types
  characterTypes: {
    numbers: boolean;
    hyphens: boolean;
    special: boolean;
    letters: boolean;
  };
  
  // Domain quality
  minQualityScore?: number;
  minSeoScore?: number;
  
  // Registration date
  registeredAfter?: string; // ISO date string
  registeredBefore?: string; // ISO date string
  
  // Domain age
  minAgeYears?: number;
  maxAgeYears?: number;
  
  // Popularity
  minSearchVolume?: number;
  minCpc?: number;
  
  // Language
  language?: string;
  
  // Sorting
  sortBy?: 'relevance' | 'price' | 'length' | 'alphabetical' | 'popularity';
  sortOrder?: 'asc' | 'desc';
}

export interface DomainSearchParams {
  // Basic search
  query: string;
  tlds?: string[];
  limit?: number;
  
  // Price filters
  min_price?: number;
  max_price?: number;
  
  // Length filters
  min_length?: number;
  max_length?: number;
  
  // Availability
  only_available?: boolean;
  only_premium?: boolean;
  
  // Domain characteristics
  starts_with?: string;
  ends_with?: string;
  contains?: string;
  exclude?: string;
  
  // Character types
  allow_numbers?: boolean;
  allow_hyphens?: boolean;
  allow_special_chars?: boolean;
  letters_only?: boolean;
  
  // Domain quality
  min_quality_score?: number;
  min_seo_score?: number;
  
  // Registration date
  registered_after?: string;
  registered_before?: string;
  
  // Domain age
  min_age_years?: number;
  max_age_years?: number;
  
  // Popularity
  min_search_volume?: number;
  min_cpc?: number;
  
  // Language
  language?: string;
  
  // Sorting
  sort_by?: 'relevance' | 'price' | 'length' | 'alphabetical' | 'popularity';
  sort_order?: 'asc' | 'desc';
}

export interface DomainSearchState {
  results: DomainSearchResult[];
  loading: boolean;
  error: string | null;
  params: DomainSearchParams;
  stats: {
    total: number;
    available: number;
    taken: number;
    premium: number;
  };
}

// Enums to match backend definitions

export type TLDTypeFE =
  | "gtld"
  | "cctld"
  | "gecctld"
  | "ngtdld"
  | "infrastructure";

export type DomainStatusFE =
  | "available"
  | "registered"
  | "reserved"
  | "premium"
  | "unknown";

export type SortOrderEnumFE = "asc" | "desc";

export type KeywordMatchTypeFE = "any" | "all" | "exact";

// Types for the new Advanced Search API Endpoint (/api/v1/domains/search)

export interface AdvancedDomainSearchRequestFE {
  /** @deprecated Use query instead */
  keywords?: string[];
  /** The search query string */
  query?: string;
  match_type?: KeywordMatchTypeFE;
  exclude_keywords?: string[];
  tlds?: string[];
  tld_types?: TLDTypeFE[];
  min_price?: number;
  max_price?: number;
  min_length?: number;
  max_length?: number;

  // Availability
  only_available?: boolean;
  only_premium?: boolean;

  // Domain characteristics
  starts_with?: string;
  ends_with?: string;
  exclude_pattern?: string;

  // Character types
  allow_numbers?: boolean;
  allow_hyphens?: boolean;
  allow_special_chars?: boolean;

  // Domain quality
  min_quality_score?: number;
  max_quality_score?: number;
  min_seo_score?: number;
  max_seo_score?: number;

  // Registration date
  registered_after?: string; // ISO datetime string
  registered_before?: string; // ISO datetime string

  // Domain age
  min_age_years?: number;
  max_age_years?: number;

  // Popularity
  min_search_volume?: number;
  max_search_volume?: number;
  min_cpc?: number;
  max_cpc?: number;

  // Language
  language_codes?: string[];

  // Sorting
  sort_by?: string; // e.g., 'price', 'length', 'name_part_length', 'quality_score', 'seo_score', 'search_volume', 'cpc', 'registered_date'
  sort_order?: SortOrderEnumFE;

  // Pagination
  page?: number;
  page_size?: number;
}

export interface FilteredDomainInfoFE {
  domain_name_full: string;
  name_part: string;
  tld_part: string;
  name_part_length: number;
  tld_type: TLDTypeFE;
  status: DomainStatusFE;
  is_available: boolean;
  is_premium: boolean;
  price?: number;
  currency?: string;
  registered_date?: string; // ISO datetime string
  quality_score?: number;
  seo_score?: number;
  search_volume?: number;
  cpc?: number;
  language?: string;
}

export interface PaginatedFilteredDomainsResponseFE {
  results: FilteredDomainInfoFE[];
  total_items: number;
  page: number;
  page_size: number;
  total_pages: number;
}
