export type ReconciliationStatus = "MATCHED" | "EXCEPTION" | "HUMAN_REVIEW" | "RESOLVED" | "UNRESOLVED";

export type InvestigationStatus = "EXPLAINED" | "HUMAN_REVIEW_REQUIRED" | "UNRESOLVED" | "MANUALLY_OVERRIDDEN";

export type ConfidenceTier = "HIGH" | "MEDIUM" | "LOW";

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  database_connected: boolean;
  ai_service_configured: boolean;
  timestamp: string;
}

export interface MetricSummary {
  totalRecords: number;
  reconciledCount: number;
  exceptionsCount: number;
  humanReviewCount: number;
  matchRatePercentage: number;
  investigationSuccessRate: number;
  avgProcessingTimeMs: number;
  totalDifferenceAmount: number;
  explainedAmount: number;
  unexplainedAmount: number;
}

export interface InvestigationItem {
  id: string;
  reconciliationId: string;
  paymentReference: string;
  orderReference: string;
  expectedAmount: number;
  actualAmount: number;
  differenceAmount: number;
  status: ReconciliationStatus;
  investigationStatus: InvestigationStatus;
  confidenceScore: number;
  confidenceTier: ConfidenceTier;
  explanation: string;
  recommendedAction: string;
  timestamp: string;
  groundTruthScenario?: string;
  isAnomaly: boolean;
}
