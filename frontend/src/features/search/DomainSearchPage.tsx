import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

type SearchResult = {
  name: string;
  domain: string;
  available: boolean;
  price?: number;
  tld: string;
  score: number;
  risk: 'low' | 'medium' | 'high';
  alternatives?: string[];
};

export const DomainSearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedTlds, setSelectedTlds] = useState<Record<string, boolean>>({
    'com': true,
    'io': true,
    'co': false,
    'ai': false,
    'app': false,
    'dev': false,
    'xyz': false,
  });
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const mockResults: SearchResult[] = [];
      
      Object.entries(selectedTlds).forEach(([tld, isSelected]) => {
        if (isSelected) {
          const domain = `${query.toLowerCase()}.${tld}`;
          const available = Math.random() > 0.3; // 70% chance of being available
          
          mockResults.push({
            name: query,
            domain,
            available,
            tld: `.${tld}`,
            score: Math.floor(Math.random() * 50) + 50, // 50-100
            risk: available ? (Math.random() > 0.7 ? 'medium' : 'low') : 'high',
            price: available ? (tld === 'com' ? 12.99 : tld === 'io' ? 59.99 : 24.99) : undefined,
            alternatives: available ? undefined : [
              `the${query}.${tld}`,
              `${query}app.${tld}`,
              `get${query}.${tld}`,
            ].slice(0, 2)
          });
        }
      });
      
      setResults(mockResults);
      setIsLoading(false);
    }, 800);
  };

  const toggleTld = (tld: string) => {
    setSelectedTlds(prev => ({
      ...prev,
      [tld]: !prev[tld]
    }));
  };

  const addToProject = (domain: string) => {
    // In a real app, this would open a modal or navigate to projects
    alert(`Added ${domain} to project`);
  };

  const addToWatchlist = (domain: string) => {
    // In a real app, this would add to watchlist
    alert(`Added ${domain} to watchlist`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Find Your Perfect Domain Name
        </h1>
        
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative rounded-md shadow-sm">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="focus:ring-indigo-500 focus:border-indigo-500 block w-full px-4 py-3 text-base border-gray-300 rounded-md"
                  placeholder="Enter a name or keyword..."
                  disabled={isLoading}
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className={`px-6 py-3 border border-transparent text-base font-medium rounded-md text-white ${
                isLoading || !query.trim() ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">TLD Filters:</p>
            <div className="flex flex-wrap gap-2">
              {Object.keys(selectedTlds).map((tld) => (
                <button
                  key={tld}
                  type="button"
                  onClick={() => toggleTld(tld)}
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    selectedTlds[tld]
                      ? 'bg-indigo-100 text-indigo-800'
                      : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                  }`}
                >
                  .{tld}
                </button>
              ))}
            </div>
          </div>
        </form>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        ) : results.length > 0 ? (
          <div className="space-y-6">
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <ul className="divide-y divide-gray-200">
                {results.map((result, index) => (
                  <li key={`${result.domain}-${index}`} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="text-lg font-medium text-gray-900">
                          {result.domain}
                        </div>
                        <span className={`ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          result.available 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {result.available ? 'Available' : 'Taken'}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {result.available && (
                          <span className="text-sm text-gray-900 font-medium">
                            ${result.price?.toFixed(2)}
                          </span>
                        )}
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          result.risk === 'high' 
                            ? 'bg-red-100 text-red-800' 
                            : result.risk === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {result.risk === 'high' ? 'High Risk' : result.risk === 'medium' ? 'Medium Risk' : 'Low Risk'}
                        </span>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Score: {result.score}/100
                        </span>
                      </div>
                    </div>
                    
                    <div className="mt-2 flex justify-between items-center">
                      <div>
                        {result.available ? (
                          <div className="flex space-x-2">
                            <button
                              onClick={() => addToProject(result.domain)}
                              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                              Add to Project
                            </button>
                            <button
                              onClick={() => addToWatchlist(result.domain)}
                              className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                              Watch
                            </button>
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500">
                            <p>Alternatives: {result.alternatives?.join(', ')}</p>
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => navigate(`/analysis?domain=${result.domain}`)}
                        className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
                      >
                        View Analysis →
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h2a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-blue-700">
                    Not finding what you're looking for? Try our advanced name generation tool or contact our support team for assistance.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : query && !isLoading ? (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
            <p className="mt-1 text-sm text-gray-500">Try adjusting your search or filter to find what you're looking for.</p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Start your domain search
              </h3>
              <div className="mt-2 max-w-xl text-sm text-gray-500">
                <p>
                  Enter a name or keyword above to check domain availability across multiple TLDs.
                </p>
              </div>
              <div className="mt-5">
                <h4 className="text-sm font-medium text-gray-900">Popular searches:</h4>
                <div className="mt-2 flex flex-wrap gap-2">
                  {['startup', 'app', 'tech', 'digital', 'labs', 'studio'].map((term) => (
                    <button
                      key={term}
                      onClick={() => setQuery(term)}
                      className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      {term}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DomainSearchPage;
