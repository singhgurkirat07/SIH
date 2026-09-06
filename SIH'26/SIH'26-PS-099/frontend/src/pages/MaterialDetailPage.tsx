import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMaterial } from '../api';
import { ArrowLeft, Building2, Tag, Scale, Factory, FileText } from 'lucide-react';
import type { Material } from '../types';

const MaterialDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [material, setMaterial] = useState<Material | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (id) {
      getMaterial(parseInt(id))
        .then(res => setMaterial(res.data))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return <div className="p-12 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-700"></div></div>;
  }

  if (!material) {
    return <div className="p-8 text-center text-gray-500">Material not found</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/materials" className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800 mb-4">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Materials
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-gray-900">{material.material_code}</h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                {material.cpse}
              </span>
            </div>
            <p className="text-gray-600 max-w-3xl">{material.description}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px px-6" aria-label="Tabs">
            {['overview', 'matches', 'nmc_mapping', 'audit_history'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`whitespace-nowrap py-4 px-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-800 flex items-center">
                      <FileText className="w-4 h-4 mr-2 text-gray-500" />
                      Normalized Attributes
                    </h3>
                  </div>
                  <div className="p-4">
                    {material.attributes && material.attributes.length > 0 ? (
                      <div className="grid grid-cols-2 gap-y-4 gap-x-8">
                        {material.attributes.map(attr => (
                          <div key={attr.id} className="border-b border-gray-100 pb-2">
                            <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">{attr.attribute_name}</dt>
                            <dd className="text-sm font-semibold text-gray-900">{attr.attribute_value}</dd>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No normalized attributes extracted yet.</p>
                    )}
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-800 flex items-center">
                      <FileText className="w-4 h-4 mr-2 text-gray-500" />
                      Normalized Description (AI Generated)
                    </h3>
                  </div>
                  <div className="p-4 bg-blue-50/30">
                    <p className="text-sm text-gray-800 font-medium">
                      {material.normalized_description || <span className="text-gray-400 italic">Pending normalization</span>}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-800">Master Data Details</h3>
                  </div>
                  <div className="p-4 space-y-4">
                    <div className="flex items-start">
                      <Tag className="w-4 h-4 mt-0.5 mr-3 text-gray-400" />
                      <div>
                        <p className="text-xs text-gray-500 font-medium">Category</p>
                        <p className="text-sm text-gray-900">{material.category || '-'}</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <Scale className="w-4 h-4 mt-0.5 mr-3 text-gray-400" />
                      <div>
                        <p className="text-xs text-gray-500 font-medium">Base Unit</p>
                        <p className="text-sm text-gray-900">{material.unit || '-'}</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <Factory className="w-4 h-4 mt-0.5 mr-3 text-gray-400" />
                      <div>
                        <p className="text-xs text-gray-500 font-medium">Manufacturer</p>
                        <p className="text-sm text-gray-900">{material.manufacturer || '-'}</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <Building2 className="w-4 h-4 mt-0.5 mr-3 text-gray-400" />
                      <div>
                        <p className="text-xs text-gray-500 font-medium">Source CPSE</p>
                        <p className="text-sm text-gray-900">{material.cpse}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-800">Procurement Insights</h3>
                  </div>
                  <div className="p-4 space-y-4">
                    <div className="flex justify-between items-center">
                      <p className="text-sm text-gray-500">Annual Volume</p>
                      <p className="text-sm font-semibold text-gray-900">{material.historical_quantity ? material.historical_quantity.toLocaleString() : '-'}</p>
                    </div>
                    <div className="flex justify-between items-center">
                      <p className="text-sm text-gray-500">Est. Unit Cost</p>
                      <p className="text-sm font-semibold text-gray-900">{material.historical_cost ? `₹${material.historical_cost.toLocaleString()}` : '-'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'matches' && (
            <div className="text-center py-12">
              <p className="text-gray-500">Matching details will appear here</p>
            </div>
          )}
          
          {activeTab === 'nmc_mapping' && (
            <div className="text-center py-12">
              <p className="text-gray-500">NMC Mapping tree will appear here</p>
            </div>
          )}

          {activeTab === 'audit_history' && (
            <div className="text-center py-12">
              <p className="text-gray-500">Audit timeline will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MaterialDetailPage;
