import React from 'react';
import type { AdminProject } from './types';

type ProjectStatus = 'all' | 'active' | 'archived' | 'deleted';

interface ProjectsTabProps {
  projects: AdminProject[];
  loading: boolean;
  error: string | null;
  projectSearchQuery: string;
  selectedProjectStatus: ProjectStatus;
  onProjectSearch: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onProjectStatusChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onProjectAction: (projectId: number, action: 'archive' | 'restore' | 'delete') => void;
}

const projectStatusOptions: { value: ProjectStatus; label: string }[] = [
  { value: 'all', label: 'All Statuses' },
  { value: 'active', label: 'Active' },
  { value: 'archived', label: 'Archived' },
  { value: 'deleted', label: 'Deleted' }
];

const ProjectsTab: React.FC<ProjectsTabProps> = ({
  projects,
  loading,
  error,
  projectSearchQuery,
  selectedProjectStatus,
  onProjectSearch,
  onProjectStatusChange,
  onProjectAction
}) => {
  const filteredProjects = React.useMemo(() => {
    return projects.filter(project => {
      const searchLower = projectSearchQuery.toLowerCase();
      const matchesSearch = project.name.toLowerCase().includes(searchLower) ||
                         (project.owner?.email?.toLowerCase() || '').includes(searchLower);
      
      const matchesStatus = selectedProjectStatus === 'all' || 
                          project.status === selectedProjectStatus;
      
      return matchesSearch && matchesStatus;
    });
  }, [projects, projectSearchQuery, selectedProjectStatus]);

  if (loading) {
    return <div className="text-center py-8">Loading projects...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-8">{error}</div>;
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h2 className="text-xl font-semibold">Projects Management</h2>
        <div className="mt-4 md:mt-0 flex space-x-4">
          <div className="relative">
            <select
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={selectedProjectStatus}
              onChange={onProjectStatusChange}
            >
              {projectStatusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="relative">
            <input
              type="text"
              placeholder="Search projects..."
              className="block w-full pl-4 pr-10 py-2 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={projectSearchQuery}
              onChange={onProjectSearch}
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Owner
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th scope="col" className="relative px-6 py-3">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredProjects.map((project) => (
              <tr key={project.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{project.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{project.owner?.email || 'N/A'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    project.status === 'active' ? 'bg-green-100 text-green-800' :
                    project.status === 'archived' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {project.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(project.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex space-x-2 justify-end">
                    {project.status === 'active' ? (
                      <>
                        <button
                          onClick={() => onProjectAction(project.id, 'archive')}
                          className="text-yellow-600 hover:text-yellow-900"
                        >
                          Archive
                        </button>
                        <button
                          onClick={() => onProjectAction(project.id, 'delete')}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </>
                    ) : project.status === 'archived' ? (
                      <>
                        <button
                          onClick={() => onProjectAction(project.id, 'restore')}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Restore
                        </button>
                        <button
                          onClick={() => onProjectAction(project.id, 'delete')}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => onProjectAction(project.id, 'restore')}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Restore
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ProjectsTab;
