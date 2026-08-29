export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// --- Types ---
export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  database: string;
  timestamp: string;
}

export interface DemoStatus {
  is_initialized: boolean;
  total_records: number;
  matched_count: number;
  exception_count: number;
  anomalies_count: number;
  investigations_ready: number;
  demo_version: string;
  seed: number;
}

export interface FeaturedCase {
  id: string;
  reconciliation_id: string;
  payment_id: string;
  payment_reference: string | null;
  classification: string;
  discrepancy_amount: string;
  reconciliation_status: string;
  confidence_tier: string;
  system_confidence: number;
  headline: string;
  recommendation: string;
}

export interface ReconciliationSummary {
  total_records: number;
  matched_count: number;
  exception_count: number;
  missing_bank_count: number;
  missing_settlement_count: number;
  duplicate_count: number;
  review_count: number;
  match_rate_percentage: number;
  total_expected_amount: string;
  total_actual_amount: string;
  total_discrepancy_amount: string;
  total_explained_by_rules_amount: string;
  total_unresolved_amount: string;
  classification_breakdown: Record<string, number>;
  operational_warnings_count: number;
}

export interface ReconciliationItem {
  id: string;
  payment_id: string;
  order_id: string | null;
  settlement_id: string | null;
  bank_transaction_id: string | null;
  order_reference: string | null;
  payment_reference: string | null;
  settlement_reference: string | null;
  bank_reference: string | null;
  utr_number: string | null;
  expected_settlement_amount: string;
  actual_settlement_amount: string | null;
  expected_bank_amount: string;
  actual_bank_amount: string | null;
  discrepancy_amount: string;
  matching_score: number;
  matching_method: string;
  status: "MATCHED" | "EXCEPTION" | "MISSING_SETTLEMENT" | "MISSING_BANK_TRANSACTION" | "DUPLICATE" | "REVIEW" | "RESOLVED" | "UNRESOLVED";
  classification: string;
  operational_warning: string | null;
  evidence_payload: any;
  reconciled_at: string;
}

export interface AnomalySummary {
  total_evaluated: number;
  anomalies_detected: number;
  anomaly_rate_percentage: number;
  severity_breakdown: Record<string, number>;
  avg_normalized_score: number;
  top_detected_signals: Record<string, number>;
  model_version: string;
}

export interface AnomalyItem {
  id: string;
  reconciliation_id: string;
  payment_id: string;
  order_reference: string | null;
  payment_reference: string | null;
  merchant_id: string | null;
  merchant_name: string | null;
  payment_amount: string;
  discrepancy_amount: string;
  reconciliation_status: string;
  reconciliation_classification: string;
  raw_anomaly_score: number;
  normalized_score: number;
  severity: "LOW" | "MEDIUM" | "HIGH";
  is_anomaly: boolean;
  detected_features: Record<string, any>;
  explanation_signals: string[];
  model_version: string;
  created_at: string;
}

export interface InvestigationSummary {
  total_investigations: number;
  explained_count: number;
  partially_explained_count: number;
  human_review_count: number;
  conflicting_evidence_count: number;
  avg_system_confidence: number;
  cached_rate_percentage: number;
}

export interface InvestigationItem {
  id: string;
  reconciliation_id: string;
  payment_id: string;
  order_reference: string | null;
  payment_reference: string | null;
  merchant_id: string | null;
  merchant_name: string | null;
  payment_amount: string;
  discrepancy_amount: string;
  reconciliation_status: string;
  reconciliation_classification: string;
  investigation_status: "EXPLAINED" | "PARTIALLY_EXPLAINED" | "HUMAN_REVIEW_REQUIRED" | "CONFLICTING_EVIDENCE" | "MANUALLY_OVERRIDDEN" | "UNRESOLVED";
  summary: string;
  facts: Array<{ statement: string; evidence_ids: string[] }>;
  explanation: string;
  evidence_references: string[];
  missing_evidence: string[];
  ai_confidence: number;
  system_confidence: number;
  confidence_tier: "HIGH" | "MEDIUM" | "LOW";
  recommended_action: string;
  human_override: boolean;
  reviewer_note: string | null;
  cached: boolean;
  latency_ms: number;
  model_name: string;
  created_at: string;
  updated_at: string;
}

export interface AuditLogItem {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string;
  previous_state: any;
  new_state: any;
  notes: string | null;
  created_at: string;
}

export interface AssistantResponse {
  query: string;
  answer: string;
  intent: string;
  retrieved_data_summary: Record<string, any>;
  evidence_sources: string[];
  confidence: number;
}

export interface DemoLoadResponse {
  status: string;
  num_clusters: number;
  records_loaded: number;
  reconciled_count: number;
  anomalies_detected: number;
  investigations_preloaded: number;
  duration_ms: number;
  cached: boolean;
  summary: {
    match_rate: string;
    matched_count: number;
    exception_count: number;
    total_discrepancy: string;
    unresolved_amount: string;
    anomalies_count: number;
  };
}

// --- API Helper ---
async function fetchJson<T>(url: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 20000);

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...options.headers,
      },
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(errBody.detail || `Request failed with status ${res.status}`);
    }

    return await res.json();
  } catch (err: any) {
    clearTimeout(timeoutId);
    throw err;
  }
}

// --- Exported Endpoints ---

export async function checkBackendHealth(): Promise<HealthResponse> {
  return fetchJson<HealthResponse>(`${API_BASE_URL}/health`);
}

export async function getDemoStatus(): Promise<DemoStatus> {
  return fetchJson<DemoStatus>(`${API_BASE_URL}/api/demo/status`);
}

export async function loadDemoDataset(
  numClusters = 1000,
  seed = 42,
  forceReset = false,
  preloadAi = true
): Promise<DemoLoadResponse> {
  return fetchJson<DemoLoadResponse>(
    `${API_BASE_URL}/api/demo/load?num_clusters=${numClusters}&seed=${seed}&force_reset=${forceReset}&preload_ai=${preloadAi}`,
    { method: "POST" }
  );
}

export async function resetDemoDatabase(): Promise<{ status: string; message: string }> {
  return fetchJson<{ status: string; message: string }>(`${API_BASE_URL}/api/demo/reset`, {
    method: "POST",
  });
}

export async function getFeaturedCases(): Promise<FeaturedCase[]> {
  return fetchJson<FeaturedCase[]>(`${API_BASE_URL}/api/demo/featured`);
}

export async function getReconciliationSummary(merchantId?: string): Promise<ReconciliationSummary> {
  const q = merchantId ? `?merchant_id=${encodeURIComponent(merchantId)}` : "";
  return fetchJson<ReconciliationSummary>(`${API_BASE_URL}/api/reconciliation/summary${q}`);
}

export async function getReconciliationResults(params?: {
  status?: string;
  classification?: string;
  has_discrepancy?: boolean;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<ReconciliationItem[]> {
  const query = new URLSearchParams();
  if (params?.status) query.append("status", params.status);
  if (params?.classification) query.append("classification", params.classification);
  if (params?.has_discrepancy !== undefined) query.append("has_discrepancy", String(params.has_discrepancy));
  if (params?.search) query.append("search", params.search);
  if (params?.limit) query.append("limit", String(params.limit));
  if (params?.offset) query.append("offset", String(params.offset));

  const q = query.toString() ? `?${query.toString()}` : "";
  return fetchJson<ReconciliationItem[]>(`${API_BASE_URL}/api/reconciliation/results${q}`);
}

export async function getReconciliationResultById(id: string): Promise<ReconciliationItem> {
  return fetchJson<ReconciliationItem>(`${API_BASE_URL}/api/reconciliation/results/${id}`);
}

export async function runReconciliation(options?: {
  merchant_id?: string;
  proximity_window_days?: number;
  sla_delay_threshold_days?: number;
  recalculate_all?: boolean;
}): Promise<any> {
  return fetchJson<any>(`${API_BASE_URL}/api/reconciliation/run`, {
    method: "POST",
    body: JSON.stringify(options || {}),
  });
}

export async function getAnomalySummary(): Promise<AnomalySummary> {
  return fetchJson<AnomalySummary>(`${API_BASE_URL}/api/anomalies/summary`);
}

export async function getAnomalyResults(params?: {
  severity?: string;
  is_anomaly?: boolean;
  min_score?: number;
  limit?: number;
  offset?: number;
}): Promise<AnomalyItem[]> {
  const query = new URLSearchParams();
  if (params?.severity) query.append("severity", params.severity);
  if (params?.is_anomaly !== undefined) query.append("is_anomaly", String(params.is_anomaly));
  if (params?.min_score !== undefined) query.append("min_score", String(params.min_score));
  if (params?.limit) query.append("limit", String(params.limit));
  if (params?.offset) query.append("offset", String(params.offset));

  const q = query.toString() ? `?${query.toString()}` : "";
  return fetchJson<AnomalyItem[]>(`${API_BASE_URL}/api/anomalies/results${q}`);
}

export async function getInvestigationSummary(): Promise<InvestigationSummary> {
  return fetchJson<InvestigationSummary>(`${API_BASE_URL}/api/investigations/summary`);
}

export async function getInvestigations(params?: {
  status?: string;
  confidence_tier?: string;
  limit?: number;
  offset?: number;
}): Promise<InvestigationItem[]> {
  const query = new URLSearchParams();
  if (params?.status) query.append("status", params.status);
  if (params?.confidence_tier) query.append("confidence_tier", params.confidence_tier);
  if (params?.limit) query.append("limit", String(params.limit));
  if (params?.offset) query.append("offset", String(params.offset));

  const q = query.toString() ? `?${query.toString()}` : "";
  return fetchJson<InvestigationItem[]>(`${API_BASE_URL}/api/investigations${q}`);
}

export async function getInvestigationById(id: string): Promise<InvestigationItem> {
  return fetchJson<InvestigationItem>(`${API_BASE_URL}/api/investigations/${id}`);
}

export async function runInvestigation(reconciliationId: string, force = false): Promise<InvestigationItem> {
  return fetchJson<InvestigationItem>(
    `${API_BASE_URL}/api/investigations/${reconciliationId}/run?force=${force}`,
    { method: "POST" }
  );
}

export async function submitHumanReview(
  investigationId: string,
  action: "RESOLVE" | "ESCALATE" | "ADD_NOTE" | "OVERRIDE_EXPLAINED",
  note: string,
  reviewer = "FINANCE_OPERATOR"
): Promise<InvestigationItem> {
  return fetchJson<InvestigationItem>(`${API_BASE_URL}/api/investigations/${investigationId}/review`, {
    method: "POST",
    body: JSON.stringify({ action, note, reviewer }),
  });
}

export async function getInvestigationAuditLogs(investigationId: string): Promise<AuditLogItem[]> {
  return fetchJson<AuditLogItem[]>(`${API_BASE_URL}/api/investigations/${investigationId}/audit-logs`);
}

export async function queryFinanceAssistant(query: string, merchantId?: string): Promise<AssistantResponse> {
  return fetchJson<AssistantResponse>(`${API_BASE_URL}/api/assistant/query`, {
    method: "POST",
    body: JSON.stringify({ query, merchant_id: merchantId }),
  });
}
