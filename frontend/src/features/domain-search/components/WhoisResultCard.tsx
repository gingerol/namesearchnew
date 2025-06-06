import React from 'react';
import type { DomainSearchResult } from '../types';

interface WhoisResultCardProps {
  result: DomainSearchResult;
  className?: string;
}

export const WhoisResultCard: React.FC<WhoisResultCardProps> = ({ 
  result,
  className = '' 
}) => {
  if (!result.whois_data) {
    return null;
  }

  const { whois_data } = result;
  const hasDetails = whois_data.registrar || whois_data.registrant_name || whois_data.registrant_organization;

  return (
    <div className={`bg-white shadow overflow-hidden sm:rounded-lg ${className}`}>
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          WHOIS Information for {result.domain}
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          {result.is_available ? 'Domain is available' : 'Domain is registered'}
        </p>
      </div>
      
      <div className="px-4 py-5 sm:p-6">
        {hasDetails ? (
          <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
            {whois_data.registrar && (
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Registrar</dt>
                <dd className="mt-1 text-sm text-gray-900">{whois_data.registrar}</dd>
              </div>
            )}
            
            {whois_data.registrant_name && (
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Registrant</dt>
                <dd className="mt-1 text-sm text-gray-900">{whois_data.registrant_name}</dd>
              </div>
            )}
            
            {whois_data.registrant_organization && (
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Organization</dt>
                <dd className="mt-1 text-sm text-gray-900">{whois_data.registrant_organization}</dd>
              </div>
            )}
            
            {whois_data.registrant_email && (
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <a href={`mailto:${whois_data.registrant_email}`} className="text-blue-600 hover:underline">
                    {whois_data.registrant_email}
                  </a>
                </dd>
              </div>
            )}
            
            {whois_data.created_date && (
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Creation Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(whois_data.created_date).toLocaleDateString()}
                </dd>
              </div>
            )}
            
            {whois_data.expiry_date && (
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Expiry Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(whois_data.expiry_date).toLocaleDateString()}
                </dd>
              </div>
            )}
            
            {whois_data.name_servers && whois_data.name_servers.length > 0 && (
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Name Servers</dt>
                <dd className="mt-1 text-sm text-gray-900 space-y-1">
                  {whois_data.name_servers.map((ns, i) => (
                    <div key={i} className="font-mono">{ns}</div>
                  ))}
                </dd>
              </div>
            )}
          </dl>
        ) : (
          <div className="text-center py-4">
            <p className="text-gray-500">
              {result.is_available 
                ? 'No registration information available for this domain.'
                : 'No detailed WHOIS information available for this domain.'}
            </p>
          </div>
        )}
      </div>
      
      {whois_data.raw_data && (
        <div className="px-4 py-4 bg-gray-50 border-t border-gray-200">
          <details className="group">
            <summary className="flex items-center justify-between cursor-pointer text-sm font-medium text-gray-700">
              <span>View Raw WHOIS Data</span>
              <span className="ml-2 text-gray-500 group-open:rotate-180">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </span>
            </summary>
            <pre className="mt-2 p-4 bg-white rounded-md overflow-auto text-xs text-gray-800">
              {whois_data.raw_data}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};
