import { cn } from '../../../lib/utils';
import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from '@heroicons/react/20/solid';

type StatCardProps = {
  name: string;
  value: string | number;
  change?: string;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon?: React.ReactNode;
  className?: string;
};

export const StatCard = ({
  name,
  value,
  change,
  changeType = 'neutral',
  icon,
  className,
}: StatCardProps) => {
  return (
    <div className={cn('bg-white overflow-hidden rounded-lg px-4 py-5 sm:p-6', className)}>
      <div className="flex items-center">
        {icon && <div className="flex-shrink-0 mr-4">{icon}</div>}
        <div>
          <dt className="text-sm font-medium text-gray-500 truncate">{name}</dt>
          <dd className="mt-1 flex items-baseline">
            <div className="text-2xl font-semibold text-gray-900">{value}</div>
            {change && (
              <div
                className={cn(
                  'ml-2 flex items-baseline text-sm font-medium',
                  changeType === 'increase' ? 'text-green-600' : '',
                  changeType === 'decrease' ? 'text-red-600' : 'text-gray-500'
                )}
              >
                {changeType === 'increase' && (
                  <ArrowUpIcon className="h-4 w-4 flex-shrink-0 self-center" aria-hidden="true" />
                )}
                {changeType === 'decrease' && (
                  <ArrowDownIcon className="h-4 w-4 flex-shrink-0 self-center" aria-hidden="true" />
                )}
                {changeType === 'neutral' && (
                  <MinusIcon className="h-4 w-4 flex-shrink-0 self-center" aria-hidden="true" />
                )}
                <span className="sr-only">
                  {changeType === 'increase' ? 'Increased' : changeType === 'decrease' ? 'Decreased' : 'No change'} by
                </span>
                {change}
              </div>
            )}
          </dd>
        </div>
      </div>
    </div>
  );
};
