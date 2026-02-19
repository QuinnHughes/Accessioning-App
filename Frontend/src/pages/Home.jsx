import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Accessioning App
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Welcome to the Accessioning Application. This application helps you manage the physical accessioning process for storage facilities.
        </p>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <strong>Getting Started:</strong> Begin by <Link to="/projects" className="underline font-semibold">creating or selecting a project</Link> to organize your accessioning work. Configure your database connection using the settings button at the bottom of the sidebar.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <Link to="/projects" className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">📋 Projects</h3>
              <p className="mt-2 text-sm text-gray-500">
                Manage accessioning projects and their categories.
              </p>
            </div>
          </Link>

          <Link to="/empty-shelves" className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">📚 Empty Shelves</h3>
              <p className="mt-2 text-sm text-gray-500">
                Record and track empty shelf locations.
              </p>
            </div>
          </Link>

          <Link to="/accessioning" className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">🏷️ Accessioning</h3>
              <p className="mt-2 text-sm text-gray-500">
                Generate barcodes and labels for new items.
              </p>
            </div>
          </Link>

          <Link to="/batch-print" className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">🖨️ Batch Printing</h3>
              <p className="mt-2 text-sm text-gray-500">
                Generate labels for multiple shelves at once.
              </p>
            </div>
          </Link>

          <Link to="/upload" className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">📤 Upload/Export</h3>
              <p className="mt-2 text-sm text-gray-500">
                Import or export accessioning data.
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
