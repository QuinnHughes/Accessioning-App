import { useState, useEffect } from 'react';
import apiFetch from '../api/client';

const ConnectionManager = ({ isOpen, onClose }) => {
  const [connectionType, setConnectionType] = useState('postgresql');
  const [config, setConfig] = useState({
    host: 'localhost',
    port: '5432',
    database: 'accessioning_app',
    username: '',
    password: ''
  });
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [currentConnection, setCurrentConnection] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadCurrentConnection();
    }
  }, [isOpen]);

  const loadCurrentConnection = async () => {
    try {
      const data = await apiFetch('/database/connection');
      setCurrentConnection(data);
      if (data.type) {
        setConnectionType(data.type);
      }
      if (data.config) {
        setConfig({
          host: data.config.host || 'localhost',
          port: data.config.port || '5432',
          database: data.config.database || 'accessioning_app',
          username: data.config.username || '',
          password: '' // Never send password back
        });
      }
    } catch (err) {
      console.error('Error loading connection:', err);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const data = await apiFetch('/database/test', {
        method: 'POST',
        body: JSON.stringify({
          type: connectionType,
          config: connectionType === 'postgresql' ? config : null
        })
      });
      setTestResult({ success: true, message: data.message || 'Connection successful!' });
    } catch (err) {
      setTestResult({ success: false, message: err.message || 'Connection test failed' });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSyncResult(null);
    try {
      const data = await apiFetch('/database/connection', {
        method: 'POST',
        body: JSON.stringify({
          type: connectionType,
          config: connectionType === 'postgresql' ? config : null
        })
      });
      alert(`✓ ${data.message}\n\nDatabase connection switched successfully!`);
      onClose();
      // Optionally reload the page to refresh all components
      window.location.reload();
    } catch (err) {
      alert(`Failed to save configuration: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadCarts = async () => {
    if (connectionType === 'sqlite') {
      setSyncResult({ success: false, message: 'Already on SQLite. Switch to PostgreSQL first.' });
      return;
    }

    setSyncing(true);
    setSyncResult(null);
    try {
      // Export from current database (PostgreSQL)
      const exportRes = await apiFetch('/database/export-carts');
      if (!exportRes.ok) {
        throw new Error('Failed to export carts');
      }
      const exportData = await exportRes.json();

      if (exportData.count === 0) {
        setSyncResult({ success: false, message: 'No carts to download' });
        return;
      }

      // Download as JSON file
      const dataStr = JSON.stringify(exportData.carts, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `sudoc-carts-backup-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);

      setSyncResult({ 
        success: true, 
        message: `✓ Exported ${exportData.count} carts to file!\n\nNow switch to SQLite and use the Upload button to import.`
      });
    } catch (err) {
      setSyncResult({ success: false, message: `Export failed: ${err.message}` });
    } finally {
      setSyncing(false);
    }
  };

  const handleUploadCarts = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      // Create file input
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.json';
      
      input.onchange = async (e) => {
        try {
          const file = e.target.files[0];
          if (!file) {
            setSyncResult({ success: false, message: 'No file selected' });
            setSyncing(false);
            return;
          }

          const text = await file.text();
          const cartsToImport = JSON.parse(text);

          // Import carts
          const importRes = await apiFetch('/database/import-carts', {
            method: 'POST',
            body: JSON.stringify(cartsToImport)
          });

          if (!importRes.ok) {
            throw new Error('Failed to import carts');
          }

          const importData = await importRes.json();
          setSyncResult({ 
            success: true, 
            message: `✓ Imported ${importData.imported} carts!\nSkipped ${importData.skipped} duplicates.`
          });
          
          setTimeout(() => window.location.reload(), 2000);
        } catch (err) {
          setSyncResult({ success: false, message: `Import failed: ${err.message}` });
        } finally {
          setSyncing(false);
        }
      };

      input.click();
    } catch (err) {
      setSyncResult({ success: false, message: `Upload failed: ${err.message}` });
      setSyncing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4 border-b pb-4">
          <h2 className="text-2xl font-bold text-gray-800">Database Connection</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {currentConnection && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
            <p className="text-sm text-green-800">
              <strong>Current:</strong> {currentConnection.type === 'sqlite' ? 'SQLite (Local)' : `PostgreSQL - ${currentConnection.config?.database}`}
            </p>
          </div>
        )}

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Database Type
          </label>
          <select
            value={connectionType}
            onChange={(e) => setConnectionType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="sqlite">SQLite (Local/Offline)</option>
            <option value="postgresql">PostgreSQL (Remote)</option>
          </select>
        </div>

        {connectionType === 'postgresql' && (
          <div className="space-y-3 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Host
              </label>
              <input
                type="text"
                value={config.host}
                onChange={(e) => setConfig({ ...config, host: e.target.value })}
                placeholder="localhost or IP address"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Port
              </label>
              <input
                type="text"
                value={config.port}
                onChange={(e) => setConfig({ ...config, port: e.target.value })}
                placeholder="5432"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Database Name
              </label>
              <input
                type="text"
                value={config.database}
                onChange={(e) => setConfig({ ...config, database: e.target.value })}
                placeholder="sudoc_isolated"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                value={config.username}
                onChange={(e) => setConfig({ ...config, username: e.target.value })}
                placeholder="postgres"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={config.password}
                onChange={(e) => setConfig({ ...config, password: e.target.value })}
                placeholder="Enter password"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>
        )}

        {connectionType === 'sqlite' && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
            <p className="text-sm text-blue-800">
              SQLite will store data locally on this computer. Great for offline work!
            </p>
          </div>
        )}

        {testResult && (
          <div className={`mb-4 p-3 rounded ${
            testResult.success 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            <p className="text-sm whitespace-pre-line">{testResult.message}</p>
          </div>
        )}

        {syncResult && (
          <div className={`mb-4 p-3 rounded ${
            syncResult.success 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            <p className="text-sm whitespace-pre-line">{syncResult.message}</p>
          </div>
        )}

        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
          <h3 className="font-semibold text-blue-900 mb-2">🔄 Sync Carts</h3>
          <div className="flex gap-2">
            <button
              onClick={handleDownloadCarts}
              disabled={syncing || connectionType === 'sqlite'}
              className="flex-1 px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              title="Export carts to a JSON file for backup"
            >
              {syncing ? '⏳ Exporting...' : '⬇️ Export to File'}
            </button>
            <button
              onClick={handleUploadCarts}
              disabled={syncing}
              className="flex-1 px-3 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              title="Import carts from a JSON file"
            >
              {syncing ? '⏳ Importing...' : '⬆️ Import from File'}
            </button>
          </div>
          <p className="text-xs text-blue-700 mt-2">
            Export carts from PostgreSQL, switch to SQLite, then import the file to work offline.
          </p>
        </div>

        <div className="flex gap-2 mt-6 pt-4 border-t border-gray-200">
          <button
            onClick={handleTest}
            disabled={testing || (connectionType === 'postgresql' && !config.username)}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {testing ? 'Testing...' : 'Test Connection'}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || (connectionType === 'postgresql' && !config.username)}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save & Switch'}
          </button>
        </div>

        <p className="text-xs text-gray-500 mt-3 text-center">
          Connection switches immediately - no restart needed
        </p>
      </div>
    </div>
  );
};

export default ConnectionManager;
