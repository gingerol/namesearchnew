import { Layout } from '../../components/layout/Layout';
import { 
  StatCard,
  AlertList,
  ProjectList,
  QuickActions,
  TrendChart,
  generateSampleData 
} from './components';
import { cn } from '../../lib/utils';
import { 
  ClockIcon, 
  ChartBarIcon, 
  DocumentTextIcon,
  GlobeAltIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

// Mock data
const stats = [
  { 
    name: 'Projects', 
    value: '5', 
    change: '+2', 
    changeType: 'increase' as const,
    icon: <DocumentTextIcon className="h-6 w-6 text-indigo-500" />
  },
  { 
    name: 'Watched Domains', 
    value: '24', 
    change: '+8', 
    changeType: 'increase' as const,
    icon: <GlobeAltIcon className="h-6 w-6 text-blue-500" />
  },
  { 
    name: 'Available Credits', 
    value: '850', 
    change: '-150', 
    changeType: 'decrease' as const,
    icon: <CurrencyDollarIcon className="h-6 w-6 text-green-500" />
  },
  { 
    name: 'Team Members', 
    value: '3', 
    change: '0', 
    changeType: 'neutral' as const,
    icon: <UserGroupIcon className="h-6 w-6 text-purple-500" />
  },
];

const recentProjects = [
  { 
    id: 1, 
    name: 'Project Alpha', 
    updated: '3 days ago', 
    count: 8,
    description: 'New SaaS platform naming project'
  },
  { 
    id: 2, 
    name: 'Brand Refresh', 
    updated: '1 week ago', 
    count: 12,
    description: 'Rebranding initiative for Q4 2023'
  },
  { 
    id: 3, 
    name: 'New Venture', 
    updated: '2 weeks ago', 
    count: 4,
    description: 'Startup naming project'
  },
];

const watchlistAlerts = [
  { 
    id: 1, 
    message: 'domain.com is now available', 
    type: 'domain' as const, 
    time: '2 hours ago',
    action: () => console.log('View domain')
  },
  { 
    id: 2, 
    message: 'New trademark filed for "xyz"', 
    type: 'trademark' as const, 
    time: '1 day ago',
    action: () => console.log('View trademark')
  },
  { 
    id: 3, 
    message: 'Price drop for premium domain', 
    type: 'price' as const, 
    time: '3 days ago',
    action: () => console.log('View price drop')
  },
  { 
    id: 4, 
    message: 'Domain backorder successful: example.ai', 
    type: 'success' as const, 
    time: '1 week ago',
    action: () => console.log('View domain')
  },
];

// Generate sample data for the trend chart
const trendData = generateSampleData(7, 2);

const DashboardPage: React.FC = () => {
  return (
    <Layout>
      {/* Header */}
      <div className="pb-5 border-b border-gray-200">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Welcome back! Here's what's happening with your names and projects.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mt-6">
        <QuickActions maxItems={4} />
      </div>

      {/* Stats Overview */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Overview</h2>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <StatCard
              key={stat.name}
              name={stat.name}
              value={stat.value}
              change={stat.change}
              changeType={stat.changeType}
              icon={stat.icon}
            />
          ))}
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Projects */}
        <ProjectList 
          projects={recentProjects} 
          viewAllHref="/projects"
          title="Recent Projects"
          emptyMessage="You don't have any projects yet. Create your first project to get started."
        />

        {/* Watchlist Alerts */}
        <AlertList
          title="Watchlist Alerts"
          alerts={watchlistAlerts}
          viewAllHref="/watchlist"
          emptyMessage="No recent alerts. Your watchlist updates will appear here."
        />
      </div>

      {/* Naming Trends */}
      <div className="mt-8">
        <div className="bg-white shadow overflow-hidden rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Naming Trends</h3>
              <a
                href="/trends"
                className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
              >
                View detailed trends
              </a>
            </div>
          </div>
          <div className="p-6">
            <div className="h-80 -mx-2 -my-2">
              <TrendChart 
                data={trendData}
                title="Naming Trends (Last 7 Days)" 
              />
            </div>
            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900">Top Trend</h4>
                <p className="mt-1 text-sm text-gray-600">"-ify" suffix +15%</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900">Popular Industry</h4>
                <p className="mt-1 text-sm text-gray-600">SaaS & Technology</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900">Avg. Name Length</h4>
                <p className="mt-1 text-sm text-gray-600">8.2 characters</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8">
        <div className="bg-white shadow overflow-hidden rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
              <a
                href="/activity"
                className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
              >
                View all activity
              </a>
            </div>
          </div>
          <div className="p-6">
            <div className="flow-root">
              <ul className="-mb-8">
                {[
                  {
                    id: 1,
                    type: 'search',
                    content: 'Searched for "cloud" domains',
                    date: 'Just now',
                    icon: <MagnifyingGlassIcon className="h-5 w-5 text-blue-500" />,
                  },
                  {
                    id: 2,
                    type: 'project',
                    content: 'Created new project "Cloud Solutions"',
                    date: '2 hours ago',
                    icon: <DocumentTextIcon className="h-5 w-5 text-green-500" />,
                  },
                  {
                    id: 3,
                    type: 'watchlist',
                    content: 'Added "cloudsync.com" to watchlist',
                    date: '5 hours ago',
                    icon: <ClockIcon className="h-5 w-5 text-yellow-500" />,
                  },
                  {
                    id: 4,
                    type: 'analysis',
                    content: 'Generated brand analysis report',
                    date: '1 day ago',
                    icon: <ChartBarIcon className="h-5 w-5 text-purple-500" />,
                  },
                ].map((activity, activityIdx) => (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      {activityIdx !== 3 ? (
                        <span
                          className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span
                            className={cn(
                              'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white',
                              {
                                'bg-blue-100': activity.type === 'search',
                                'bg-green-100': activity.type === 'project',
                                'bg-yellow-100': activity.type === 'watchlist',
                                'bg-purple-100': activity.type === 'analysis',
                              }
                            )}
                          >
                            {activity.icon}
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-gray-800">
                              {activity.content}
                            </p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-gray-500">
                            <time dateTime={activity.date}>
                              {activity.date}
                            </time>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

// Export as default for React.lazy and other dynamic imports
export default DashboardPage;
