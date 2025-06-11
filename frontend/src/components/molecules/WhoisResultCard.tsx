import React from 'react';
import LoadingSpinner from '../atoms/LoadingSpinner';
import Badge from '../atoms/Badge';

interface WhoisData {
  domain: string;
  registrar: string;
  creationDate: string;
  expirationDate: string;
  status: string[];
  nameServers: string[];
}

interface WhoisResultCardProps {
  data?: WhoisData;
  loading: boolean;
  error?: string;
  className?: string;
}

const WhoisResultCard: React.FC<WhoisResultCardProps> = ({
  data,
  loading,
  error,
  className = '',
}) => {
  if (loading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="flex items-center justify-center">
          <LoadingSpinner size="md" color="blue" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="text-red-500 text-sm">{error}</div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="text-lg font-medium text-gray-900">{data.domain}</div>
        <Badge variant="info">{data.status[0]}</Badge>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-600">Registrar</span>
          <span className="text-gray-900">{data.registrar}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-600">Creation Date</span>
          <span className="text-gray-900">{new Date(data.creationDate).toLocaleDateString()}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-600">Expiration Date</span>
          <span className="text-gray-900">{new Date(data.expirationDate).toLocaleDateString()}</span>
        </div>

        <div>
          <span className="text-gray-600">Name Servers</span>
          <div className="mt-2 space-y-1">
            {data.nameServers.map((ns, index) => (
              <span key={index} className="text-gray-900">{ns}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhoisResultCard;
