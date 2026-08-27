import time
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from app.models.schema import (
    Payment,
    Order,
    Fee,
    Tax,
    Refund,
    Settlement,
    BankTransaction,
    ReconciliationResult,
    AnomalyResult,
    AnomalySeverity,
)
from app.anomaly.features import AnomalyFeatureExtractor
from app.anomaly.signals import AnomalySignalGenerator
from app.anomaly.schemas import (
    AnomalySummaryResponse,
    AnomalyRunResult,
    AnomalyRunRequest,
)


class IsolationForestAnomalyDetector:
    """
    Unsupervised ML Anomaly Detection Engine using Scikit-Learn Isolation Forest.
    Fits population baseline on observable features, scores multi-dimensional outliers,
    and assigns 0-100 normalized anomaly scores and severity tiers.
    """

    def __init__(
        self,
        contamination: float = 0.10,
        n_estimators: int = 100,
        random_state: int = 42,
        high_severity_threshold: float = 70.0,
        medium_severity_threshold: float = 40.0,
        model_version: str = "isolation_forest_v1.0",
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.high_severity_threshold = high_severity_threshold
        self.medium_severity_threshold = medium_severity_threshold
        self.model_version = model_version

        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            max_samples="auto",
            random_state=self.random_state,
            n_jobs=-1,
        )

    def fit_and_score(
        self,
        feature_matrix: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Fits Isolation Forest on feature matrix and produces:
        - raw_scores: continuous scores (lower = more anomalous)
        - normalized_scores: scaled from 0.0 (normal) to 100.0 (extreme outlier)
        - predictions: -1 (anomaly), 1 (inlier)
        """
        if len(feature_matrix) == 0:
            return np.array([]), np.array([]), np.array([])

        self.model.fit(feature_matrix)
        raw_scores = self.model.score_samples(feature_matrix)
        preds = self.model.predict(feature_matrix)

        # Normalize raw scores to 0-100 (where 100 is most anomalous)
        min_score = np.min(raw_scores)
        max_score = np.max(raw_scores)
        denom = max_score - min_score if (max_score - min_score) > 1e-6 else 1.0

        normalized_scores = ((max_score - raw_scores) / denom) * 100.0
        normalized_scores = np.clip(normalized_scores, 0.0, 100.0)

        return raw_scores, normalized_scores, preds

    def run_detection(
        self,
        db: Session,
        clear_existing: bool = True
    ) -> AnomalyRunResult:
        """
        Runs feature extraction and Isolation Forest against all reconciliation results in DB.
        """
        start_time = time.perf_counter()

        # 1. Fetch observable database entities
        reconciliation_results: List[ReconciliationResult] = db.query(ReconciliationResult).all()
        if not reconciliation_results:
            return AnomalyRunResult(
                status="no_records",
                processed_count=0,
                anomalies_found=0,
                duration_ms=0.0,
                summary=AnomalySummaryResponse(),
            )

        payments_by_id = {p.id: p for p in db.query(Payment).all()}
        orders_by_id = {o.id: o for o in db.query(Order).all()}
        fees_by_payment_id: Dict[str, List[Fee]] = {}
        for f in db.query(Fee).all():
            fees_by_payment_id.setdefault(f.payment_id, []).append(f)

        taxes_by_payment_id: Dict[str, List[Tax]] = {}
        for t in db.query(Tax).all():
            taxes_by_payment_id.setdefault(t.payment_id, []).append(t)

        refunds_by_payment_id: Dict[str, List[Refund]] = {}
        for r in db.query(Refund).all():
            refunds_by_payment_id.setdefault(r.payment_id, []).append(r)

        settlements_by_id = {s.id: s for s in db.query(Settlement).all()}
        bank_by_id = {b.id: b for b in db.query(BankTransaction).all()}

        # 2. Extract Feature Matrix
        feature_matrix, feature_dicts, rec_ids = AnomalyFeatureExtractor.extract_features(
            reconciliation_results=reconciliation_results,
            payments_by_id=payments_by_id,
            orders_by_id=orders_by_id,
            fees_by_payment_id=fees_by_payment_id,
            taxes_by_payment_id=taxes_by_payment_id,
            refunds_by_payment_id=refunds_by_payment_id,
            settlements_by_id=settlements_by_id,
            bank_by_id=bank_by_id,
        )

        # 3. Model Fit & Predict
        raw_scores, normalized_scores, preds = self.fit_and_score(feature_matrix)

        if clear_existing:
            db.query(AnomalyResult).delete()
            db.commit()

        anomaly_records: List[AnomalyResult] = []
        anomalies_count = 0

        for i, rec_id in enumerate(rec_ids):
            raw_val = float(raw_scores[i])
            norm_val = float(normalized_scores[i])
            is_anomaly = bool(preds[i] == -1 or norm_val >= self.high_severity_threshold)

            if is_anomaly:
                anomalies_count += 1

            if norm_val >= self.high_severity_threshold:
                sev = AnomalySeverity.HIGH
            elif norm_val >= self.medium_severity_threshold:
                sev = AnomalySeverity.MEDIUM
            else:
                sev = AnomalySeverity.LOW

            signals = AnomalySignalGenerator.generate_signals(
                features=feature_dicts[i],
                raw_score=raw_val,
                normalized_score=norm_val,
            )

            anom_res = AnomalyResult(
                id=f"anom_{rec_id.replace('rec_', '')}",
                reconciliation_id=rec_id,
                raw_anomaly_score=Decimal(f"{raw_val:.5f}"),
                normalized_score=Decimal(f"{norm_val:.2f}"),
                severity=sev,
                is_anomaly=is_anomaly,
                detected_features=feature_dicts[i],
                explanation_signals=signals,
                model_version=self.model_version,
                created_at=datetime.utcnow(),
            )
            anomaly_records.append(anom_res)

        db.add_all(anomaly_records)
        db.commit()

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        summary = self.compute_summary(db)

        return AnomalyRunResult(
            status="success",
            processed_count=len(anomaly_records),
            anomalies_found=anomalies_count,
            duration_ms=round(elapsed_ms, 2),
            summary=summary,
        )

    @classmethod
    def compute_summary(cls, db: Session) -> AnomalySummaryResponse:
        results: List[AnomalyResult] = db.query(AnomalyResult).all()
        total = len(results)
        if total == 0:
            return AnomalySummaryResponse()

        anom_count = sum(1 for r in results if r.is_anomaly)
        sev_counts: Dict[str, int] = {}
        top_signals: Dict[str, int] = {}
        total_score = 0.0

        for r in results:
            sev_key = r.severity.value if hasattr(r.severity, "value") else str(r.severity)
            sev_counts[sev_key] = sev_counts.get(sev_key, 0) + 1
            total_score += float(r.normalized_score)

            for sig in (r.explanation_signals or []):
                top_signals[sig] = top_signals.get(sig, 0) + 1

        # Keep top 5 signals
        sorted_top_signals = dict(sorted(top_signals.items(), key=lambda x: -x[1])[:5])

        return AnomalySummaryResponse(
            total_evaluated=total,
            anomalies_detected=anom_count,
            anomaly_rate_percentage=round((anom_count / total) * 100.0, 2),
            severity_breakdown=sev_counts,
            avg_normalized_score=round(total_score / total, 2),
            top_detected_signals=sorted_top_signals,
            model_version=results[0].model_version if results else "isolation_forest_v1.0",
        )
