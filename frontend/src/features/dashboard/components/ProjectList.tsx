import { Link } from 'react-router-dom';
import { cn } from '../../../lib/utils';
import { FolderIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline';

type Project = {
  id: string | number;
  name: string;
  updated: string;
  count: number;
  description?: string;
};

type ProjectListProps = {
  projects: Project[];
  viewAllHref?: string;
  className?: string;
  emptyMessage?: string;
  title?: string;
};

export const ProjectList = ({
  projects,
  viewAllHref,
  className,
  emptyMessage = 'No projects to display',
  title = 'Recent Projects',
}: ProjectListProps) => {
  return (
    <div className={cn('bg-white shadow overflow-hidden rounded-lg', className)}>
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          {viewAllHref && (
            <Link
              to={viewAllHref}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
            >
              View all
            </Link>
          )}
        </div>
      </div>
      <div className="divide-y divide-gray-200">
        {projects.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {projects.map((project) => (
              <li key={project.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <FolderIcon className="h-6 w-6 text-indigo-400" />
                  </div>
                  <div className="ml-3 flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {project.name}
                      </h4>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        {project.count} {project.count === 1 ? 'item' : 'items'}
                      </span>
                    </div>
                    {project.description && (
                      <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                        {project.description}
                      </p>
                    )}
                    <div className="mt-2 flex items-center text-xs text-gray-500">
                      <span>Updated {project.updated}</span>
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <Link
                      to={`/projects/${project.id}`}
                      className="inline-flex items-center rounded-md bg-white text-sm font-medium text-indigo-600 hover:text-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    >
                      <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                      <span className="sr-only">View project</span>
                    </Link>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="px-6 py-8 text-center">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No projects</h3>
            <p className="mt-1 text-sm text-gray-500">
              {emptyMessage}
            </p>
            <div className="mt-6">
              <Link
                to="/projects/new"
                className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
                New Project
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Add missing PlusIcon component
const PlusIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 20 20"
    fill="currentColor"
    aria-hidden="true"
  >
    <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
  </svg>
);
