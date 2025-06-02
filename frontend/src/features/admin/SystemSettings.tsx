import React, { useState } from 'react';

export const SystemSettings: React.FC = () => {
  const [settings, setSettings] = useState({
    siteName: 'Namesearch.io',
    supportEmail: 'support@namesearch.io',
    defaultUserCredits: 1000,
    enableTrendAnalysis: true,
    enableLegalPrescreening: true,
    enableBrandSimulation: false,
    enableWatchlist: true,
    defaultRateLimit: 100,
    maxBatchSize: 50,
    maintenanceMode: false,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? Number(value) : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Save settings to API
    alert('Settings saved successfully!');
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">System Settings</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">General Settings</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">Basic configuration for your application.</p>
          </div>
          
          <div className="px-4 py-5 sm:p-6 space-y-6">
            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-3">
                <label htmlFor="siteName" className="block text-sm font-medium text-gray-700">
                  Site Name
                </label>
                <input
                  type="text"
                  name="siteName"
                  id="siteName"
                  value={settings.siteName}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="supportEmail" className="block text-sm font-medium text-gray-700">
                  Support Email
                </label>
                <input
                  type="email"
                  name="supportEmail"
                  id="supportEmail"
                  value={settings.supportEmail}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="defaultUserCredits" className="block text-sm font-medium text-gray-700">
                  Default User Credits
                </label>
                <input
                  type="number"
                  name="defaultUserCredits"
                  id="defaultUserCredits"
                  value={settings.defaultUserCredits}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
            </div>
          </div>

          <div className="px-4 py-5 sm:px-6 border-t border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Feature Flags</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">Enable or disable application features.</p>
          </div>

          <div className="px-4 py-5 sm:p-6">
            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  id="enableTrendAnalysis"
                  name="enableTrendAnalysis"
                  type="checkbox"
                  checked={settings.enableTrendAnalysis}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="enableTrendAnalysis" className="ml-3 block text-sm font-medium text-gray-700">
                  Enable Trend Analysis
                </label>
              </div>

              <div className="flex items-center">
                <input
                  id="enableLegalPrescreening"
                  name="enableLegalPrescreening"
                  type="checkbox"
                  checked={settings.enableLegalPrescreening}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="enableLegalPrescreening" className="ml-3 block text-sm font-medium text-gray-700">
                  Enable Legal Pre-screening
                </label>
              </div>

              <div className="flex items-center">
                <input
                  id="enableBrandSimulation"
                  name="enableBrandSimulation"
                  type="checkbox"
                  checked={settings.enableBrandSimulation}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="enableBrandSimulation" className="ml-3 block text-sm font-medium text-gray-700">
                  Enable Brand Simulation (Beta)
                </label>
              </div>

              <div className="flex items-center">
                <input
                  id="enableWatchlist"
                  name="enableWatchlist"
                  type="checkbox"
                  checked={settings.enableWatchlist}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="enableWatchlist" className="ml-3 block text-sm font-medium text-gray-700">
                  Enable Watchlist
                </label>
              </div>
            </div>
          </div>

          <div className="px-4 py-5 sm:px-6 border-t border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">API Settings</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">Configure API rate limits and behavior.</p>
          </div>

          <div className="px-4 py-5 sm:p-6">
            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-3">
                <label htmlFor="defaultRateLimit" className="block text-sm font-medium text-gray-700">
                  Default Rate Limit (requests/minute)
                </label>
                <input
                  type="number"
                  name="defaultRateLimit"
                  id="defaultRateLimit"
                  value={settings.defaultRateLimit}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="maxBatchSize" className="block text-sm font-medium text-gray-700">
                  Max Batch Size
                </label>
                <input
                  type="number"
                  name="maxBatchSize"
                  id="maxBatchSize"
                  value={settings.maxBatchSize}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
            </div>
          </div>

          <div className="px-4 py-5 sm:px-6 border-t border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Maintenance Mode</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Enable maintenance mode to restrict access to administrators only.
            </p>
          </div>

          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <input
                id="maintenanceMode"
                name="maintenanceMode"
                type="checkbox"
                checked={settings.maintenanceMode}
                onChange={handleInputChange}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="maintenanceMode" className="ml-3 block text-sm font-medium text-gray-700">
                Enable Maintenance Mode
              </label>
            </div>
            {settings.maintenanceMode && (
              <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-yellow-700">
                      Maintenance mode is currently enabled. Only administrators will be able to access the application.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
            <button
              type="button"
              className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Save Changes
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default SystemSettings;
