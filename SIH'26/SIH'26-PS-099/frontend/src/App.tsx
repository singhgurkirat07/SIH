import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import MaterialsPage from './pages/MaterialsPage';
import MaterialDetailPage from './pages/MaterialDetailPage';
import ReviewQueuePage from './pages/ReviewQueuePage';
import MatchingPage from './pages/MatchingPage';
import NMCRegistryPage from './pages/NMCRegistryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import MaterialFamiliesPage from './pages/MaterialFamiliesPage';
import RationalizationDashboard from './pages/RationalizationDashboard';
import AuditTrailPage from './pages/AuditTrailPage';
import APIIntegrationPage from './pages/APIIntegrationPage';
import SearchPage from './pages/SearchPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="materials" element={<MaterialsPage />} />
          <Route path="materials/:id" element={<MaterialDetailPage />} />
          <Route path="matching" element={<MatchingPage />} />
          <Route path="review" element={<ReviewQueuePage />} />
          <Route path="nmc" element={<NMCRegistryPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="material-families" element={<MaterialFamiliesPage />} />
          <Route path="rationalization" element={<RationalizationDashboard />} />
          <Route path="audit" element={<AuditTrailPage />} />
          <Route path="api-docs" element={<APIIntegrationPage />} />
          <Route path="search" element={<SearchPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
