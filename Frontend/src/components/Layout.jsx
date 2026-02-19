import { useState, useEffect } from 'react';
import { Link, Outlet } from 'react-router-dom';
import './Layout.css';
import ConnectionManager from './ConnectionManager';

const Layout = () => {
  const [showConnectionManager, setShowConnectionManager] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    // Listen for project changes
    const checkProject = () => {
      const projectId = localStorage.getItem("selectedProjectId");
      const projectName = localStorage.getItem("selectedProjectName");
      if (projectId && projectName) {
        setSelectedProject({ id: projectId, name: projectName });
      } else {
        setSelectedProject(null);
      }
    };

    checkProject();
    
    // Check periodically for changes
    const interval = setInterval(checkProject, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="layout">
      <nav className="sidebar">
        <h2>Accessioning App</h2>
        
        {selectedProject && (
          <div className="selected-project-badge">
            <strong>Active Project:</strong>
            <div className="project-name">{selectedProject.name}</div>
          </div>
        )}
      
        <h3><b>Menu</b></h3>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/projects">Projects</Link></li>
          <li><Link to="/empty-shelves">Empty Shelves</Link></li>
          <li><Link to="/accessioning">Accessioning</Link></li>
          <li><Link to="/batch-print">Batch Printing</Link></li>
          <li><Link to="/upload">Upload/Export</Link></li>
        </ul>

        <button
          onClick={() => setShowConnectionManager(true)}
          className="connection-manager-btn"
        >
          ⚙️ Database Connection
        </button>
      </nav>

      <main className="main-content">
        <div className="px-4 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>

      <ConnectionManager 
        isOpen={showConnectionManager} 
        onClose={() => setShowConnectionManager(false)} 
      />
    </div>
  );
};

export default Layout;
