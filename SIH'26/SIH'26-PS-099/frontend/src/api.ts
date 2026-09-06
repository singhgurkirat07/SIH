import axios from 'axios';
import type {
  Material,
  MatchResult,
  NMCCode,
  AuditLog,
  DashboardData,
  GoldenTestMetrics,
  BulkUploadResponse,
  RerankerStatus,
} from './types';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Health
export const getHealth = () => api.get('/health');

// Materials
export const uploadMaterials = (file: File): Promise<{ data: BulkUploadResponse }> => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/materials/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getMaterials = (params?: {
  skip?: number;
  limit?: number;
  cpse?: string;
  category?: string;
  search?: string;
}): Promise<{ data: { total: number, items: Material[] } }> => api.get('/materials', { params });

export const getMaterial = (id: number): Promise<{ data: any }> =>
  api.get(`/materials/${id}`);

export const getSampleCsv = () =>
  api.get('/materials/sample-csv', { responseType: 'blob' });

// Matching
export const runMatching = (): Promise<{ data: any }> => api.post('/match');

export const getMatches = (params?: {
  skip?: number;
  limit?: number;
  status?: string;
  match_type?: string;
  min_confidence?: number;
}): Promise<{ data: { total: number, items: MatchResult[] } }> => api.get('/matches', { params });

export const getMatch = (id: number): Promise<{ data: MatchResult }> =>
  api.get(`/matches/${id}`);

export const approveMatch = (
  id: number,
  reason?: string
): Promise<{ data: MatchResult }> =>
  api.post(`/matches/${id}/approve`, { action: 'approve', reason });

export const rejectMatch = (
  id: number,
  reason?: string
): Promise<{ data: MatchResult }> =>
  api.post(`/matches/${id}/reject`, { action: 'reject', reason });

export const getSavingsTrend = (): Promise<{ data: any[] }> =>
  api.get('/analytics/savings-trend');

// Dashboard
export const getDashboard = (): Promise<{ data: DashboardData }> =>
  api.get('/dashboard');

// NMC
export const getNMCs = (): Promise<{ data: { items: NMCCode[] } }> => api.get('/nmc');

export const getNMC = (id: number): Promise<{ data: NMCCode }> =>
  api.get(`/nmc/${id}`);

// Audit
export const getAuditLogs = (params?: {
  skip?: number;
  limit?: number;
}): Promise<{ data: { total: number, items: AuditLog[] } }> => api.get('/audit', { params });

// Search
export const searchMaterials = (
  q: string
): Promise<{ data: { items: Material[] } }> => api.get('/search', { params: { q } });

// Export
export const exportData = () =>
  api.get('/export', { responseType: 'blob' });

// Golden Test
export const runGoldenTest = (): Promise<{ data: GoldenTestMetrics }> =>
  api.post('/golden-test/run');

export const getGoldenTestResults = (): Promise<{ data: GoldenTestMetrics }> =>
  api.get('/golden-test/results');

// Reranker
export const getRerankerStatus = (): Promise<{ data: RerankerStatus }> =>
  api.get('/reranker/status');

export const trainReranker = (): Promise<{ data: any }> =>
  api.post('/reranker/train');

// Seed
export const seedDatabase = (): Promise<{ data: any }> => api.post('/seed');

export default api;
