import React, { useState } from 'react';

type ApiKey = {
  id: string;
  name: string;
  key: string;
  created: string;
  expires?: string;
  lastUsed?: string;
  permissions: string[];
};

export const ApiKeys: React.FC = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyPermissions, setNewKeyPermissions] = useState<string[]>(['read']);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'Production API',
      key: 'sk_live_1234567890abcdef',
      created: '2025-01-15',
      lastUsed: '2025-05-30',
      permissions: ['read', 'write', 'admin'],
    },
    {
      id: '2',
      name: 'Development',
      key: 'sk_test_abcdef1234567890',
      created: '2025-03-10',
      expires: '2025-12-31',
      lastUsed: '2025-05-28',
      permissions: ['read', 'write'],
    },
  ]);
  const [newKey, setNewKey] = useState<string | null>(null);

  const handleCreateKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;

    // In a real app, this would call an API to generate a key
    const generatedKey = `sk_${Math.random().toString(36).substring(2, 15)}`;
    
    const newApiKey: ApiKey = {
      id: Date.now().toString(),
      name: newKeyName,
      key: generatedKey,
      created: new Date().toISOString().split('T')[0],
      permissions: [...newKeyPermissions],
    };

    setApiKeys([newApiKey, ...apiKeys]);
    setNewKey(generatedKey);
    setNewKeyName('');
    setNewKeyPermissions(['read']);
    setShowCreateForm(false);
  };

  const handleDeleteKey = (id: string) => {
    if (window.confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      setApiKeys(apiKeys.filter(key => key.id !== id));
    }
  };

  const togglePermission = (permission: string) => {
    setNewKeyPermissions(prev =>
      prev.includes(permission)
        ? prev.filter(p => p !== permission)
        : [...prev, permission]
    );
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You might want to show a toast notification here
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">API Keys</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Create New Key
        </button>
      </div>

      {newKey && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-medium text-green-800">API Key Created</h3>
              <p className="mt-1 text-sm text-green-700">
                Make sure to copy your API key now. You won't be able to see it again!
              </p>
              <div className="mt-2 flex items-center">
                <code className="px-3 py-2 bg-white text-sm font-mono rounded border border-gray-300">
                  {newKey}
                </code>
                <button
                  onClick={() => copyToClipboard(newKey)}
                  className="ml-2 px-3 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Copy
                </button>
              </div>
            </div>
            <button
              onClick={() => setNewKey(null)}
              className="text-gray-400 hover:text-gray-500"
            >
              <span className="sr-only">Dismiss</span>
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      )}

      {showCreateForm ? (
        <div className="mb-6 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Create New API Key</h3>
          </div>
          <form onSubmit={handleCreateKey} className="p-6">
            <div className="space-y-6">
              <div>
                <label htmlFor="keyName" className="block text-sm font-medium text-gray-700">
                  Key Name
                </label>
                <input
                  type="text"
                  id="keyName"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="e.g., Production Server"
                  required
                />
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Permissions</h4>
                <div className="space-y-2">
                  {[
                    { value: 'read', label: 'Read', description: 'Read-only access to resources' },
                    { value: 'write', label: 'Write', description: 'Create and update resources' },
                    { value: 'admin', label: 'Admin', description: 'Full access including user management' },
                  ].map((permission) => (
                    <div key={permission.value} className="flex items-start">
                      <div className="flex items-center h-5">
                        <input
                          id={`permission-${permission.value}`}
                          name="permissions"
                          type="checkbox"
                          checked={newKeyPermissions.includes(permission.value)}
                          onChange={() => togglePermission(permission.value)}
                          className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                        />
                      </div>
                      <div className="ml-3 text-sm">
                        <label htmlFor={`permission-${permission.value}`} className="font-medium text-gray-700">
                          {permission.label}
                        </label>
                        <p className="text-gray-500">{permission.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Create Key
                </button>
              </div>
            </div>
          </form>
        </div>
      ) : (
        <div className="space-y-3 mb-6">
          <p className="text-sm text-gray-500">
            API keys are used to authenticate with the Namesearch API. Keep your keys secure and never share them in client-side code.
          </p>
          <p className="text-sm text-gray-500">
            <a href="#" className="text-indigo-600 hover:text-indigo-500">
              View API documentation →
            </a>
          </p>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Your API Keys</h3>
        </div>
        
        {apiKeys.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 7a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2h-4a2 2 0 01-2-2V7zM5 7a2 2 0 012-2h4a2 2 0 012 2v10a2 2 0 01-2 2H7a2 2 0 01-2-2V7z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No API keys</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating a new API key.
            </p>
            <div className="mt-6">
              <button
                type="button"
                onClick={() => setShowCreateForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg
                  className="-ml-1 mr-2 h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
                    clipRule="evenodd"
                  />
                </svg>
                New API Key
              </button>
            </div>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {apiKeys.map((apiKey) => (
              <li key={apiKey.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-indigo-600 truncate">
                        {apiKey.name}
                      </p>
                      <div className="ml-2 flex-shrink-0 flex">
                        <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          {apiKey.permissions.includes('admin') ? 'Admin' : 'Standard'}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-gray-500">
                          <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                            {apiKey.key.substring(0, 8)}...{apiKey.key.substring(apiKey.key.length - 4)}
                          </span>
                          <button
                            onClick={() => copyToClipboard(apiKey.key)}
                            className="ml-2 text-gray-400 hover:text-gray-500"
                            title="Copy to clipboard"
                          >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                            </svg>
                          </button>
                        </p>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        <p>
                          Created on <time dateTime={apiKey.created}>{new Date(apiKey.created).toLocaleDateString()}</time>
                        </p>
                        {apiKey.lastUsed && (
                          <p className="ml-4">
                            Last used <time dateTime={apiKey.lastUsed}>
                              {new Date(apiKey.lastUsed).toLocaleDateString()}
                            </time>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <button
                      onClick={() => handleDeleteKey(apiKey.id)}
                      className="font-medium text-red-600 hover:text-red-500"
                    >
                      Revoke
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ApiKeys;
