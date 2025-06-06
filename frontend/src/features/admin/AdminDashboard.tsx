import { useState } from "react";
import { Navigate } from "react-router-dom";
import ProjectsTab from "./ProjectsTab";
import type { AdminProject } from "./types";

// Type definitions
type TabType = 'overview' | 'users' | 'projects' | 'logs' | 'api-keys';
type ProjectStatus = 'all' | 'active' | 'archived' | 'deleted';

// Mock auth store - Remove when actual auth store is available
const useAuthStore = () => ({
  user: { is_superuser: true }
});

const AdminDashboard: React.FC = () => {
  const { user } = useAuthStore();
  
  // State for data
  const [projects] = useState<AdminProject[]>([]);
  const [projectSearchQuery, setProjectSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  // Search and filter states
  const [selectedProjectStatus, setSelectedProjectStatus] = useState<ProjectStatus>('all');
  
  // Handle project status change
  const handleProjectStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedProjectStatus(e.target.value as ProjectStatus);
  };
  
  // Handle project search
  const handleProjectSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProjectSearchQuery(e.target.value);
  };
  
  // Handle project actions
  const handleProjectAction = async (projectId: number, action: 'archive' | 'restore' | 'delete') => {
    try {
      setLoading(true);
      setError(null);
      console.log(`Project ${action} action for ID: ${projectId}`);
      // TODO: Implement actual API call
      // await adminApi.updateProjectStatus(projectId, action);
    } catch (err) {
      setError('Failed to update project status');
      console.error('Project action failed:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Filter projects based on search query and status
  const filteredProjects = projects.filter(project => {
    const searchLower = projectSearchQuery.toLowerCase();
    const matchesSearch = project.name.toLowerCase().includes(searchLower) ||
                       (project.owner?.email?.toLowerCase() || '').includes(searchLower);
    
    const matchesStatus = selectedProjectStatus === 'all' || project.status === selectedProjectStatus;
    
    return matchesSearch && matchesStatus;
  });

  // Redirect non-admin users
  if (!user || !user.is_superuser) {
    return <Navigate to="/" replace />;
  }

  // Render tab content based on active tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Dashboard Overview</h2>
            {/* Add overview content */}
          </div>
        );
      case 'users':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">User Management</h2>
            {/* Add users content */}
          </div>
        );
      case 'projects':
        return activeTab === 'projects' && (
          <ProjectsTab 
            projects={filteredProjects}
            loading={loading}
            error={error}
            projectSearchQuery={projectSearchQuery}
            selectedProjectStatus={selectedProjectStatus}
            onProjectSearch={handleProjectSearch}
            onProjectStatusChange={handleProjectStatusChange}
            onProjectAction={handleProjectAction}
          />
        );
      case 'logs':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">System Logs</h2>
            {/* Add logs content */}
          </div>
        );
      case 'api-keys':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">API Keys</h2>
            {/* Add API keys content */}
          </div>
        );
      default:
        return null;
    }
  };

  // Render tab navigation
  const renderTabs = () => {
    const tabs: { id: TabType; label: string }[] = [
      { id: 'overview', label: 'Overview' },
      { id: 'users', label: 'Users' },
      { id: 'projects', label: 'Projects' },
      { id: 'logs', label: 'Logs' },
      { id: 'api-keys', label: 'API Keys' },
    ];

    return (
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    );
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
      </div>
      
      {renderTabs()}
      <div className="bg-white shadow rounded-lg p-6 mt-6">
        {renderTabContent()}
      </div>
    </div>
  );
};

// Export as default for React.lazy and other dynamic imports
export default AdminDashboard;
