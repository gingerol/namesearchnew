import { useState } from 'react';
import { Layout } from '../../components/layout/Layout';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';

type TimeRange = '7d' | '30d' | '90d' | '1y';

interface TrendData {
  date: string;
  searches: number;
  available: number;
  registered: number;
}

interface CategoryData {
  name: string;
  value: number;
  color: string;
}

interface PopularSearch {
  id: number;
  term: string;
  count: number;
  change: number;
}

const TrendsPage = () => {
  const [timeRange, setTimeRange] = useState<TimeRange>('30d');
  
  // Mock data - replace with actual data fetching
  const trendData: TrendData[] = [
    { date: 'Jan', searches: 4000, available: 2400, registered: 1600 },
    { date: 'Feb', searches: 3000, available: 1398, registered: 1602 },
    { date: 'Mar', searches: 2000, available: 9800, registered: 10200 },
    { date: 'Apr', searches: 2780, available: 3908, registered: 1872 },
    { date: 'May', searches: 1890, available: 4800, registered: 4100 },
    { date: 'Jun', searches: 2390, available: 3800, registered: 3400 },
  ];

  const categoryData: CategoryData[] = [
    { name: '.com', value: 45, color: '#3B82F6' },
    { name: '.io', value: 25, color: '#10B981' },
    { name: '.ai', value: 15, color: '#8B5CF6' },
    { name: 'Other', value: 15, color: '#F59E0B' },
  ];

  const popularSearches: PopularSearch[] = [
    { id: 1, term: 'nexify', count: 1243, change: 12.5 },
    { id: 2, term: 'zenith', count: 987, change: -3.2 },
    { id: 3, term: 'quantum', count: 876, change: 24.1 },
    { id: 4, term: 'vortex', count: 765, change: 8.7 },
    { id: 5, term: 'lumina', count: 654, change: -5.4 },
  ];

  return (
    <Layout>
      <div className="pb-5 border-b border-gray-200">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Naming Trends</h1>
            <p className="mt-2 text-sm text-gray-600">
              Analyze naming trends and domain availability statistics.
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <div className="inline-flex rounded-md shadow-sm">
              {[
                { value: '7d', label: '7d' },
                { value: '30d', label: '30d' },
                { value: '90d', label: '90d' },
                { value: '1y', label: '1y' },
              ].map((range) => (
                <button
                  key={range.value}
                  type="button"
                  onClick={() => setTimeRange(range.value as TimeRange)}
                  className={`${timeRange === range.value
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-700 hover:bg-gray-50'
                    } px-4 py-2 text-sm font-medium border border-gray-300 first:rounded-l-md last:rounded-r-md focus:z-10 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500`}
                >
                  {range.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { name: 'Total Searches', value: '12,345', change: '+12%', changeType: 'increase' },
          { name: 'Available Domains', value: '8,234', change: '+5%', changeType: 'increase' },
          { name: 'Registered Domains', value: '4,111', change: '-3%', changeType: 'decrease' },
          { name: 'Avg. Search Volume', value: '412', change: '+24%', changeType: 'increase' },
        ].map((stat, statIdx) => (
          <div key={statIdx} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">{stat.value}</dd>
              <div className={`mt-1 flex items-baseline text-sm ${stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'}`}>
                {stat.changeType === 'increase' ? (
                  <svg className="self-center flex-shrink-0 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="self-center flex-shrink-0 h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                <span className="sr-only">{stat.changeType === 'increase' ? 'Increased' : 'Decreased'} by</span>
                {stat.change}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Search Trends */}
        <div className="bg-white p-6 rounded-lg shadow col-span-2">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Search Volume Trends</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="searches" stroke="#3B82F6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} name="Searches" />
                <Line type="monotone" dataKey="available" stroke="#10B981" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} name="Available" />
                <Line type="monotone" dataKey="registered" stroke="#8B5CF6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} name="Registered" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Domain Categories */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Domain TLD Distribution</h2>
          <div className="h-80 flex flex-col items-center">
            <div className="w-full h-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-4 w-full">
              {categoryData.map((category, index) => (
                <div key={index} className="flex items-center">
                  <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: category.color }} />
                  <span className="text-sm text-gray-600">{category.name}</span>
                  <span className="ml-auto text-sm font-medium text-gray-900">{category.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Popular Searches */}
      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Popular Searches</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">Most searched terms in the last 30 days</p>
        </div>
        <div className="bg-white overflow-hidden">
          <ul className="divide-y divide-gray-200">
            {popularSearches.map((search) => (
              <li key={search.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <p className="text-sm font-medium text-indigo-600 truncate">
                      {search.term}
                    </p>
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                      {search.count} searches
                    </span>
                  </div>
                  <div className="ml-2 flex-shrink-0 flex">
                    <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${search.change >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {search.change >= 0 ? '↑' : '↓'} {Math.abs(search.change)}%
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Layout>
  );
};

export { TrendsPage };
