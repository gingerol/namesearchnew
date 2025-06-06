import { cn } from '../../../lib/utils';
import { BellAlertIcon, ExclamationTriangleIcon, CurrencyDollarIcon, GlobeAltIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { DocumentTextIcon } from '@heroicons/react/20/solid';

type AlertType = 'info' | 'warning' | 'success' | 'error' | 'domain' | 'trademark' | 'price';

type Alert = {
  id: string | number;
  message: string;
  time: string;
  type: AlertType;
  action?: () => void;
};

type AlertListProps = {
  title: string;
  alerts: Alert[];
  viewAllHref?: string;
  className?: string;
  emptyMessage?: string;
};

export const AlertList = ({
  title,
  alerts,
  viewAllHref,
  className,
  emptyMessage = 'No alerts to display',
}: AlertListProps) => {
  const getAlertIcon = (type: AlertType) => {
    switch (type) {
      case 'warning':
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />;
      case 'domain':
        return <GlobeAltIcon className="h-5 w-5 text-blue-400" />;
      case 'trademark':
        return <DocumentTextIcon className="h-5 w-5 text-purple-400" />;
      case 'price':
        return <CurrencyDollarIcon className="h-5 w-5 text-green-400" />;
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-400" />;
      default:
        return <BellAlertIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className={cn('bg-white shadow overflow-hidden rounded-lg', className)}>
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          {viewAllHref && (
            <a
              href={viewAllHref}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
            >
              View all
            </a>
          )}
        </div>
      </div>
      <div className="divide-y divide-gray-200">
        {alerts.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <li key={alert.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start">
                  <div className="flex-shrink-0 pt-0.5">
                    {getAlertIcon(alert.type)}
                  </div>
                  <div className="ml-3 flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{alert.message}</p>
                    <p className="mt-1 text-xs text-gray-500">{alert.time}</p>
                  </div>
                  {alert.action && (
                    <button
                      onClick={alert.action}
                      className="ml-4 flex-shrink-0 text-sm font-medium text-indigo-600 hover:text-indigo-500"
                    >
                      View
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="px-6 py-4 text-center text-sm text-gray-500">
            {emptyMessage}
          </div>
        )}
      </div>
    </div>
  );
};
