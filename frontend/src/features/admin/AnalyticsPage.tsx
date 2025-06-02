import React from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export const AnalyticsPage: React.FC = () => {
  // Mock data for user growth
  const userGrowthData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'New Users',
        data: [65, 59, 80, 81, 56, 72],
        borderColor: 'rgb(79, 70, 229)',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        tension: 0.3,
        fill: true,
      },
    ],
  };

  // Mock data for feature usage
  const featureUsageData = {
    labels: ['Search', 'Analysis', 'Watchlist', 'Projects', 'Trends'],
    datasets: [
      {
        label: 'Feature Usage',
        data: [1200, 800, 600, 400, 300],
        backgroundColor: [
          'rgba(79, 70, 229, 0.7)',
          'rgba(99, 102, 241, 0.7)',
          'rgba(129, 140, 248, 0.7)',
          'rgba(165, 180, 252, 0.7)',
          'rgba(199, 210, 254, 0.7)',
        ],
        borderColor: [
          'rgba(79, 70, 229, 1)',
          'rgba(99, 102, 241, 1)',
          'rgba(129, 140, 248, 1)',
          'rgba(165, 180, 252, 1)',
          'rgba(199, 210, 254, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // Chart options
  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'User Growth (Last 6 Months)',
      },
    },
  };

  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Feature Usage (Last 30 Days)',
      },
    },
  };

  // Mock data for top searches
  const topSearches = [
    { term: 'Brandify', count: 245 },
    { term: 'Nexify', count: 189 },
    { term: 'Omnibrand', count: 156 },
    { term: 'Zenmark', count: 132 },
    { term: 'Innovate', count: 98 },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Analytics Dashboard</h2>
        <div className="flex space-x-4">
          <select className="px-4 py-2 border rounded-md bg-white">
            <option>Last 30 Days</option>
            <option>Last 90 Days</option>
            <option>This Year</option>
            <option>All Time</option>
          </select>
          <button className="px-4 py-2 bg-white border rounded-md hover:bg-gray-50">
            Export Data
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Users" 
          value="1,245" 
          change="+12.5%" 
          changeType="increase" 
          icon="people"
        />
        <StatCard 
          title="Active Projects" 
          value="3,782" 
          change="+8.2%" 
          changeType="increase" 
          icon="folder"
        />
        <StatCard 
          title="API Calls" 
          value="28.5K" 
          change="+24.1%" 
          changeType="increase" 
          icon="api"
        />
        <StatCard 
          title="Avg. Session" 
          value="4m 32s" 
          change="-2.3%" 
          changeType="decrease" 
          icon="timer"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <Line options={lineOptions} data={userGrowthData} />
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <Bar options={barOptions} data={featureUsageData} />
        </div>
      </div>

      {/* Top Searches */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Search Terms</h3>
        <div className="space-y-4">
          {topSearches.map((search, index) => (
            <div key={index} className="flex items-center">
              <div className="w-8 h-8 flex items-center justify-center bg-indigo-100 text-indigo-800 rounded-full font-medium">
                {index + 1}
              </div>
              <div className="ml-4 flex-1">
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-900">{search.term}</span>
                  <span className="text-sm text-gray-500">{search.count} searches</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div 
                    className="bg-indigo-600 h-2 rounded-full" 
                    style={{ width: `${(search.count / topSearches[0].count) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard: React.FC<{
  title: string;
  value: string;
  change: string;
  changeType: 'increase' | 'decrease';
  icon: string;
}> = ({ title, value, change, changeType, icon }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <div className="flex items-center">
      <div className="p-3 rounded-full bg-indigo-100 text-indigo-600">
        <span className="material-icons">{icon}</span>
      </div>
      <div className="ml-4">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <div className="flex items-center">
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          <span className={`ml-2 text-sm font-medium ${
            changeType === 'increase' ? 'text-green-600' : 'text-red-600'
          }`}>
            {change}
          </span>
        </div>
      </div>
    </div>
  </div>
);

export default AnalyticsPage;
