import React, { useState } from 'react';
import { BellAlertIcon, BellSlashIcon, CheckCircleIcon, ExclamationCircleIcon, ClockIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';
import { Layout } from '../../components/layout/Layout';

type AlertType = 'all' | 'domain' | 'trademark' | 'price';

interface WatchlistItem {
  id: number;
  name: string;
  type: 'domain' | 'trademark' | 'price';
  message: string;
  time: string;
  read: boolean;
  metadata?: Record<string, any>;
}

export const WatchlistPage = () => {
  const [activeTab, setActiveTab] = useState<AlertType>('all');
  const [items, setItems] = useState<WatchlistItem[]>([
    {
      id: 1,
      name: 'nexify.com',
      type: 'domain',
      message: 'Domain is now available for registration',
      time: '2 hours ago',
      read: false,
      metadata: {
        status: 'available',
        tld: 'com',
      },
    },
    {
      id: 2,
      name: 'Brandify',
      type: 'trademark',
      message: 'New trademark application detected',
      time: '1 day ago',
      read: false,
      metadata: {
        status: 'pending',
        class: '35, 42',
        country: 'US',
      },
    },
    {
      id: 3,
      name: 'zenmark.io',
      type: 'price',
      message: 'Price drop for premium domain',
      time: '3 days ago',
      read: true,
      metadata: {
        oldPrice: 2499,
        newPrice: 1999,
        currency: 'USD',
      },
    },
  ]);

  const filteredItems = activeTab === 'all' 
    ? items 
    : items.filter(item => item.type === activeTab);

  const markAsRead = (id: number) => {
    setItems(items.map(item => 
      item.id === id ? { ...item, read: true } : item
    ));
  };

  const markAllAsRead = () => {
    setItems(items.map(item => ({ ...item, read: true })));
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'domain':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'trademark':
        return <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />;
      case 'price':
        return <CurrencyDollarIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <Layout>
      <div className="pb-5 border-b border-gray-200">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Watchlist</h1>
            <p className="mt-2 text-sm text-gray-600">
              Monitor domains, trademarks, and pricing changes.
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <button
              type="button"
              onClick={markAllAsRead}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Mark all as read
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { name: 'All', type: 'all', count: items.length },
            { name: 'Domains', type: 'domain', count: items.filter(i => i.type === 'domain').length },
            { name: 'Trademarks', type: 'trademark', count: items.filter(i => i.type === 'trademark').length },
            { name: 'Price Drops', type: 'price', count: items.filter(i => i.type === 'price').length },
          ].map((tab) => (
            <button
              key={tab.type}
              onClick={() => setActiveTab(tab.type as AlertType)}
              className={`${activeTab === tab.type
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              {tab.name}
              {tab.count > 0 && (
                <span
                  className={`${activeTab === tab.type ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-900'
                    } hidden ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium md:inline-block`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Alerts list */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md mt-6">
        <ul className="divide-y divide-gray-200">
          {filteredItems.length > 0 ? (
            filteredItems.map((item) => (
              <li key={item.id} className={!item.read ? 'bg-blue-50' : 'bg-white'}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      {getIcon(item.type)}
                    </div>
                    <div className="ml-3 flex-1">
                      <div className="flex items-center justify-between">
                        <p className={`text-sm font-medium ${!item.read ? 'text-gray-900' : 'text-gray-500'}`}>
                          {item.name}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <p className="text-xs text-gray-500">{item.time}</p>
                        </div>
                      </div>
                      <p className="mt-1 text-sm text-gray-500">{item.message}</p>
                      {item.metadata && (
                        <div className="mt-2 flex space-x-4 text-xs text-gray-500">
                          {Object.entries(item.metadata).map(([key, value]) => (
                            <span key={key}>
                              {key}: <span className="font-medium">{value}</span>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    {!item.read && (
                      <div className="ml-4 flex-shrink-0">
                        <button
                          type="button"
                          onClick={() => markAsRead(item.id)}
                          className="text-gray-400 hover:text-gray-500"
                        >
                          <BellSlashIcon className="h-5 w-5" aria-hidden="true" />
                          <span className="sr-only">Mark as read</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </li>
            ))
          ) : (
            <li className="py-12 text-center">
              <BellAlertIcon className="mx-auto h-12 w-12 text-gray-400" aria-hidden="true" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No alerts</h3>
              <p className="mt-1 text-sm text-gray-500">
                {activeTab === 'all' 
                  ? 'You have no alerts in your watchlist.'
                  : `You have no ${activeTab} alerts.`}
              </p>
            </li>
          )}
        </ul>
      </div>
    </Layout>
  );
};

export default WatchlistPage;
