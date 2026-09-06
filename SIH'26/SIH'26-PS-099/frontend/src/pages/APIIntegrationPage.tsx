import React from 'react';
import { Download, ExternalLink } from 'lucide-react';
import { exportData } from '../api';

const APIIntegrationPage: React.FC = () => {

  const handleExport = async () => {
    try {
      const res = await exportData();
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'numm_export.json');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">API & Integration</h1>
          <p className="text-sm text-gray-500 mt-1">Connect CPSE ERPs to the Unified Material Master</p>
        </div>
        <button 
          onClick={handleExport}
          className="flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50"
        >
          <Download className="w-4 h-4 mr-2" />
          Export All Data
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Architecture</h2>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 font-mono text-sm text-center">
          <div className="flex justify-between items-center max-w-3xl mx-auto">
            <div className="bg-blue-100 text-blue-800 p-3 rounded-lg border border-blue-200">
              CPSE SAP / ERP
            </div>
            <div className="text-gray-400 font-bold">→ REST API →</div>
            <div className="bg-purple-100 text-purple-800 p-3 rounded-lg border border-purple-200">
              Integration Layer
            </div>
            <div className="text-gray-400 font-bold">→ Internal →</div>
            <div className="bg-green-100 text-green-800 p-3 rounded-lg border border-green-200">
              AI Matching Engine
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-800">REST Endpoints</h2>
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="flex items-center text-sm font-medium text-blue-600 hover:text-blue-800">
            View Swagger UI <ExternalLink className="w-4 h-4 ml-1" />
          </a>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-white">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Endpoint</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            <tr>
              <td className="px-6 py-4 whitespace-nowrap"><span className="px-2 py-1 text-xs font-bold text-green-700 bg-green-100 rounded">GET</span></td>
              <td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-gray-600">/api/materials</td>
              <td className="px-6 py-4 text-sm text-gray-500">List all materials with optional filtering</td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap"><span className="px-2 py-1 text-xs font-bold text-blue-700 bg-blue-100 rounded">POST</span></td>
              <td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-gray-600">/api/materials/upload</td>
              <td className="px-6 py-4 text-sm text-gray-500">Bulk upload via CSV</td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap"><span className="px-2 py-1 text-xs font-bold text-green-700 bg-green-100 rounded">GET</span></td>
              <td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-gray-600">/api/nmc</td>
              <td className="px-6 py-4 text-sm text-gray-500">Retrieve all assigned National Material Codes</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default APIIntegrationPage;
