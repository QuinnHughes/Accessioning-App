import { useState, useEffect } from 'react';
import { apiFetch } from '../api/client';

export default function UploadExport() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [items, setItems] = useState([]);
  const [startRange, setStartRange] = useState('');
  const [endRange, setEndRange] = useState('');
  const [totalCount, setTotalCount] = useState(0);

  const projectId = localStorage.getItem('selectedProjectId');
  const projectName = localStorage.getItem('selectedProjectName');

  useEffect(() => {
    if (projectId) {
      loadItems();
    }
  }, [projectId]);

  const loadItems = async () => {
    try {
      const data = await apiFetch(`/items?project_id=${projectId}`);
      const itemsArray = Array.isArray(data) ? data : [];
      setItems(itemsArray);
      setTotalCount(itemsArray.length);
    } catch (error) {
      console.error('Failed to load items:', error);
      setItems([]);
      setTotalCount(0);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.xlsx') && !selectedFile.name.endsWith('.xls')) {
        alert('Please select an Excel file (.xlsx or .xls)');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    try {
      setUploading(true);
      const response = await fetch('http://localhost:8000/api/items/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      const result = await response.json();
      alert(`Successfully uploaded ${result.items_count} items`);
      setFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
      
      loadItems();
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleExport = async () => {
    try {
      let url = `http://localhost:8000/api/items/export?project_id=${projectId}`;
      
      if (startRange && endRange) {
        url += `&start_range=${encodeURIComponent(startRange)}&end_range=${encodeURIComponent(endRange)}`;
      }

      const response = await fetch(url);
      
      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      
      const filename = startRange && endRange
        ? `accessioned_items_${projectName}_${startRange.replace(/\//g, '-')}_to_${endRange.replace(/\//g, '-')}.xlsx`
        : `accessioned_items_${projectName}_all.xlsx`;
      
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed: ' + error.message);
    }
  };

  const filterItems = async () => {
    if (!startRange || !endRange) {
      loadItems();
      return;
    }

    try {
      const data = await apiFetch(
        `/items?project_id=${projectId}&start_range=${encodeURIComponent(startRange)}&end_range=${encodeURIComponent(endRange)}`
      );
      setItems(data);
    } catch (error) {
      console.error('Failed to filter items:', error);
      alert('Failed to filter items');
    }
  };

  const clearFilter = () => {
    setStartRange('');
    setEndRange('');
    loadItems();
  };

  if (!projectId) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Please select a project from the Projects page first.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Upload & Export</h1>
        <p className="mt-2 text-sm text-gray-700">
          Project: <span className="font-semibold">{projectName}</span>
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Upload Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Accessioned Items</h3>
          <p className="text-sm text-gray-600 mb-4">
            Upload Excel files with barcode and alternative_call_number columns that were generated
            during accessioning and filled with barcodes.
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Excel File
              </label>
              <input
                id="file-input"
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>

            {file && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p className="text-sm text-blue-800">
                  <strong>Selected:</strong> {file.name}
                </p>
                <p className="text-xs text-blue-600 mt-1">
                  Size: {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Upload File'}
            </button>
          </div>
        </div>

        {/* Export Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Export Accessioned Items</h3>
          <p className="text-sm text-gray-600 mb-4">
            Export all uploaded items or filter by alternative call number range.
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Range (Optional)
              </label>
              <input
                type="text"
                value={startRange}
                onChange={(e) => setStartRange(e.target.value)}
                placeholder="e.g., S-1-01B-01-01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Range (Optional)
              </label>
              <input
                type="text"
                value={endRange}
                onChange={(e) => setEndRange(e.target.value)}
                placeholder="e.g., S-1-15B-08-07"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={filterItems}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50"
              >
                Filter View
              </button>
              <button
                onClick={clearFilter}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50"
              >
                Clear Filter
              </button>
            </div>

            <button
              onClick={handleExport}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Export to Excel
            </button>
          </div>
        </div>
      </div>

      {/* Items Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Uploaded Items ({items.length} {totalCount > items.length ? `of ${totalCount}` : ''})
          </h3>
        </div>

        {items.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>No items uploaded yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Barcode
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Alternative Call Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded At
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {items.map((item) => (
                  <tr key={item.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.barcode}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.alternative_call_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
