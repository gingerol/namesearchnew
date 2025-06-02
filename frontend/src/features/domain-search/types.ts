// Domain search related types

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
  minPrice?: number | '';
  maxPrice?: number | '';
  minLength?: number | '';
  maxLength?: number | '';
  onlyAvailable: boolean;
  onlyPremium: boolean;
  tlds: string[];
  characterTypes: {
    numbers: boolean;
    hyphens: boolean;
    special: boolean;
  };
}

export interface DomainSearchParams {
  query: string;
  tlds?: string[];
  limit?: number;
  min_length?: number;
  max_length?: number;
  min_price?: number;
  max_price?: number;
  only_available?: boolean;
  only_premium?: boolean;
  allow_numbers?: boolean;
  allow_hyphens?: boolean;
  allow_special_chars?: boolean;
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
