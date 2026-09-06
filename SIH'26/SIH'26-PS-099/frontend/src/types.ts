export interface Material {
  id: number;
  cpse: string;
  material_code: string;
  description: string;
  normalized_description: string | null;
  category: string | null;
  material_type: string | null;
  unit: string | null;
  specification: string | null;
  manufacturer: string | null;
  historical_quantity: number | null;
  historical_cost: number | null;
  created_at: string;
  updated_at: string;
  attributes: NormalizedAttribute[];
  nmc_code?: string | null;
}

export interface NormalizedAttribute {
  id: number;
  material_id: number;
  attribute_name: string;
  attribute_value: string;
  confidence: number;
}

export interface MatchResult {
  id: number;
  material_a_id: number;
  material_b_id: number;
  match_type: string;
  confidence_score: number;
  semantic_similarity: number;
  attribute_similarity: number;
  technical_similarity: number;
  text_similarity: number;
  category_similarity: number;
  explanation: string | null;
  status: string;
  reviewed_by: string | null;
  reviewed_at: string | null;
  common_national_code: string | null;
  created_at: string;
  material_a: Material;
  material_b: Material;
}

export interface NMCCode {
  id: number;
  nmc_code: string;
  category: string;
  description: string;
  normalized_attributes: string | null;
  created_at: string;
  mappings: NMCMapping[];
}

export interface NMCMapping {
  id: number;
  nmc_id: number;
  material_id: number;
  cpse: string;
  original_code: string;
  status: string;
  created_at: string;
}

export interface AuditLog {
  id: number;
  timestamp: string;
  user: string;
  action: string;
  entity_type: string;
  entity_id: number | null;
  details: string | null;
  material_ids: string | null;
}

export interface DashboardData {
  total_materials: number;
  duplicates_detected: number;
  potential_equivalences: number;
  high_confidence_matches: number;
  pending_reviews: number;
  approved_matches: number;
  rejected_matches: number;
  total_nmc_generated: number;
  average_confidence: number;
  estimated_savings: number;
  cpse_counts: Record<string, number>;
  category_counts: Record<string, number>;
  match_type_distribution: Record<string, number>;
  confidence_distribution: Record<string, number>;
  recent_activity: AuditLog[];
}

export interface GoldenTestMetrics {
  precision: number;
  recall: number;
  f1: number;
  accuracy: number;
  total_pairs: number;
  correct_predictions: number;
}

export interface BulkUploadResponse {
  message: string;
  total_records: number;
  successful_records: number;
  failed_records: number;
  errors: Array<Record<string, unknown>> | null;
}

export interface RerankerStatus {
  trained: boolean;
  feedback_count: number;
  min_required: number;
  message: string;
}

export interface Explanation {
  reasons: Array<{
    type: string;
    detail: string;
    impact: string;
  }>;
  differences: Array<{
    type: string;
    detail: string;
    impact: string;
  }>;
  warnings?: Array<{
    type: string;
    detail: string;
  }>;
  summary: string;
  recommendation: string;
  why_not_merge?: {
    matching_attributes: any[];
    conflicting_attributes: any[];
    missing_attributes: any[];
    decision: string;
    reason: string;
  };
}
