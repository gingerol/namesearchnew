import { Link } from 'react-router-dom';
import { cn } from '../../../lib/utils';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ClockIcon,
  BellIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  DocumentDuplicateIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

type QuickAction = {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  color: string;
};

const defaultActions: QuickAction[] = [
  {
    name: 'New Search',
    href: '/search',
    icon: MagnifyingGlassIcon,
    description: 'Start a new domain search',
    color: 'bg-blue-100 text-blue-700',
  },
  {
    name: 'Add Project',
    href: '/projects/new',
    icon: PlusIcon,
    description: 'Create a new project',
    color: 'bg-green-100 text-green-700',
  },
  {
    name: 'Recent Searches',
    href: '/search/history',
    icon: ClockIcon,
    description: 'View your search history',
    color: 'bg-purple-100 text-purple-700',
  },
  {
    name: 'Watchlist',
    href: '/watchlist',
    icon: BellIcon,
    description: 'Manage your watchlist',
    color: 'bg-yellow-100 text-yellow-700',
  },
  {
    name: 'Team Members',
    href: '/team',
    icon: UserGroupIcon,
    description: 'Manage team access',
    color: 'bg-indigo-100 text-indigo-700',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Cog6ToothIcon,
    description: 'Account settings',
    color: 'bg-gray-100 text-gray-700',
  },
  {
    name: 'Templates',
    href: '/templates',
    icon: DocumentDuplicateIcon,
    description: 'Use search templates',
    color: 'bg-pink-100 text-pink-700',
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: ChartBarIcon,
    description: 'View usage analytics',
    color: 'bg-teal-100 text-teal-700',
  },
];

type QuickActionsProps = {
  actions?: QuickAction[];
  className?: string;
  title?: string;
  maxItems?: number;
};

export const QuickActions = ({
  actions = defaultActions,
  className,
  title = 'Quick Actions',
  maxItems = 4,
}: QuickActionsProps) => {
  const visibleActions = maxItems ? actions.slice(0, maxItems) : actions;

  return (
    <div className={className}>
      <h2 className="text-lg font-medium text-gray-900 mb-4">{title}</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {visibleActions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.name}
              to={action.href}
              className="group relative flex items-center space-x-3 rounded-lg border border-gray-200 bg-white px-6 py-5 shadow-sm hover:border-gray-300 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2"
            >
              <div className={cn('flex-shrink-0 rounded-md p-3', action.color)}>
                <Icon className="h-6 w-6" aria-hidden="true" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="focus:outline-none">
                  <span className="absolute inset-0" aria-hidden="true" />
                  <p className="text-sm font-medium text-gray-900">{action.name}</p>
                  <p className="truncate text-sm text-gray-500">
                    {action.description}
                  </p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};
