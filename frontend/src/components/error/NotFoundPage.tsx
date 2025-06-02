import React from 'react';
import { Link } from 'react-router-dom';
import { ExclamationTriangleIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

export const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center">
        <div className="flex justify-center">
          <div className="flex items-center justify-center w-16 h-16 rounded-full bg-red-100">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-600" aria-hidden="true" />
          </div>
        </div>
        <h1 className="mt-3 text-4xl font-extrabold text-gray-900 sm:text-5xl">404</h1>
        <h2 className="mt-3 text-2xl font-medium text-gray-900">Page not found</h2>
        <p className="mt-2 text-base text-gray-500">
          Sorry, we couldn't find the page you're looking for.
        </p>
        <div className="mt-6">
          <Link
            to="/"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <ArrowLeftIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            Go back home
          </Link>
        </div>
        <div className="mt-10">
          <p className="text-sm font-medium text-indigo-600">
            Or try one of these pages:
          </p>
          <div className="mt-4 flex justify-center space-x-4">
            <Link
              to="/dashboard"
              className="text-base font-medium text-indigo-600 hover:text-indigo-500"
            >
              Dashboard
            </Link>
            <span className="inline-block border-l border-gray-300" aria-hidden="true" />
            <Link
              to="/projects"
              className="text-base font-medium text-indigo-600 hover:text-indigo-500"
            >
              Projects
            </Link>
            <span className="inline-block border-l border-gray-300" aria-hidden="true" />
            <Link
              to="/trends"
              className="text-base font-medium text-indigo-600 hover:text-indigo-500"
            >
              Trends
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
