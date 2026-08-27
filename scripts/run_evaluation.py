import sys
import time
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List

# Add backend directory to Python path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.synthetic.generator import SyntheticFinancialDataEngine
from app.synthetic.seeder import DatabaseSeeder
from app.reconciliation.engine import DeterministicReconciliationEngine
from app.anomaly.detector import IsolationForestAnomalyDetector
from app.models.schema import ReconciliationResult, ReconciliationStatus, AnomalyResult


def run_benchmark(num_clusters: int = 1000, seed: int = 42) -> Dict[str, Any]:
    print("=" * 75)
    print("[*] LedgerLens — Dual Engine Benchmark (Deterministic + ML Anomaly)")
    print("=" * 75)
    print(f"* Benchmark Scale : {num_clusters:,} transaction clusters")
    print(f"* PRNG Seed       : {seed}")
    print("-" * 75)

    # 1. Generate Synthetic Dataset + Hidden Ground Truth
    t0 = time.perf_counter()
    engine = SyntheticFinancialDataEngine(seed=seed)
    dataset = engine.generate_dataset(num_clusters=num_clusters)
    gen_time = time.perf_counter() - t0
    print(f"[OK] Generated {num_clusters:,} ground-truth clusters in {gen_time:.3f}s")

    # 2. Setup In-Memory Isolated Database Session
    mem_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=mem_engine)
    MemSession = sessionmaker(bind=mem_engine)
    db = MemSession()

    DatabaseSeeder.seed(db, dataset, clear_existing=True)

    # 3. Run Deterministic Reconciliation Engine
    t1 = time.perf_counter()
    rec_engine = DeterministicReconciliationEngine()
    rec_run_res = rec_engine.reconcile_all(db=db, clear_existing=True)
    rec_time = time.perf_counter() - t1
    rec_throughput = num_clusters / rec_time if rec_time > 0 else 0.0
    print(f"[OK] Reconciled {num_clusters:,} records in {rec_time:.3f}s ({rec_throughput:,.1f} recs/sec)")

    # 4. Run ML Anomaly Detection (Isolation Forest)
    t2 = time.perf_counter()
    anomaly_detector = IsolationForestAnomalyDetector(contamination=0.10, random_state=seed)
    anom_run_res = anomaly_detector.run_detection(db=db, clear_existing=True)
    anom_time = time.perf_counter() - t2
    anom_throughput = num_clusters / anom_time if anom_time > 0 else 0.0
    print(f"[OK] ML Anomaly Detection scored {num_clusters:,} records in {anom_time:.3f}s ({anom_throughput:,.1f} recs/sec)")
    print("-" * 75)

    # 5. Evaluate Deterministic Reconciliation vs Hidden Ground Truth
    reconciled_results: List[ReconciliationResult] = db.query(ReconciliationResult).order_by(ReconciliationResult.payment_id).all()
    anomaly_results_by_rec_id = {a.reconciliation_id: a for a in db.query(AnomalyResult).all()}
    ground_truth_list = dataset["ground_truth"]

    gt_by_cluster_idx = {}
    for gt in ground_truth_list:
        idx = int(gt["cluster_id"].replace("CLU_", ""))
        gt_by_cluster_idx[idx] = gt

    total_evaluated = len(reconciled_results)
    status_matches = 0
    classification_matches = 0
    amount_discrepancy_exact_matches = 0

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    scenario_metrics: Dict[str, Dict[str, Any]] = {}

    for r in reconciled_results:
        idx = int(r.payment_id.replace("pay_", ""))
        gt = gt_by_cluster_idx[idx]
        st_type = gt["scenario_type"]
        st_key = st_type.value if hasattr(st_type, "value") else str(st_type)

        scenario_metrics.setdefault(st_key, {
            "total": 0,
            "correct_status": 0,
            "correct_class": 0,
            "anomaly_scores": [],
            "high_anomalies": 0,
            "anomalies_flagged": 0,
        })
        scenario_metrics[st_key]["total"] += 1

        is_gt_exception = (gt["expected_status"] != "MATCHED")
        is_engine_exception = (r.status != ReconciliationStatus.MATCHED)

        # Status Evaluation
        status_correct = False
        if gt["expected_status"] == "MATCHED" and r.status == ReconciliationStatus.MATCHED:
            status_correct = True
        elif gt["expected_status"] == "EXCEPTION" and r.status in [
            ReconciliationStatus.EXCEPTION,
            ReconciliationStatus.MISSING_BANK_TRANSACTION,
            ReconciliationStatus.MISSING_SETTLEMENT,
            ReconciliationStatus.DUPLICATE,
            ReconciliationStatus.REVIEW,
        ]:
            status_correct = True

        if status_correct:
            status_matches += 1
            scenario_metrics[st_key]["correct_status"] += 1

        # Classification Evaluation
        gt_scenario_name = st_key
        class_correct = False
        if gt_scenario_name == "NORMAL_MATCH" and (r.classification == "NONE" or r.classification == "NORMAL_MATCH"):
            class_correct = True
        elif gt_scenario_name == "SETTLEMENT_DELAY" and (r.classification == "SETTLEMENT_DELAY" or r.operational_warning == "SETTLEMENT_DELAY"):
            class_correct = True
        elif gt_scenario_name == r.classification:
            class_correct = True
        elif gt_scenario_name == "MISSING_BANK_TRANSACTION" and (r.classification == "MISSING_BANK_TRANSACTION" or r.classification == "MISSING_BANK"):
            class_correct = True
        elif gt_scenario_name == "REFERENCE_ID_DISCREPANCY" and (r.classification == "REFERENCE_ID_DISCREPANCY" or r.classification == "REFERENCE_DISCREPANCY"):
            class_correct = True
        elif gt_scenario_name == "UNEXPLAINED_EXCEPTION" and (r.classification == "UNEXPLAINED_EXCEPTION" or r.classification == "UNEXPLAINED"):
            class_correct = True

        if class_correct:
            classification_matches += 1
            scenario_metrics[st_key]["correct_class"] += 1

        # Discrepancy Amount Exact Match
        gt_diff = Decimal(str(gt["expected_difference"]))
        if abs(r.discrepancy_amount) == abs(gt_diff) or (st_key in ["REFERENCE_ID_DISCREPANCY", "SETTLEMENT_DELAY"] and r.discrepancy_amount == Decimal("0.00")):
            amount_discrepancy_exact_matches += 1

        # Binary Confusion Matrix
        if is_gt_exception and is_engine_exception:
            tp += 1
        elif not is_gt_exception and not is_engine_exception:
            tn += 1
        elif not is_gt_exception and is_engine_exception:
            fp += 1
        elif is_gt_exception and not is_engine_exception:
            fn += 1

        # ML Anomaly metrics per scenario
        anom = anomaly_results_by_rec_id.get(r.id)
        if anom:
            score = float(anom.normalized_score)
            scenario_metrics[st_key]["anomaly_scores"].append(score)
            if score >= 70.0:
                scenario_metrics[st_key]["high_anomalies"] += 1
            if anom.is_anomaly:
                scenario_metrics[st_key]["anomalies_flagged"] += 1

    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 1.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 1.0

    print("[*] PART 1: DETERMINISTIC RECONCILIATION ENGINE BASELINE")
    print(f"  * Status Accuracy               : {(status_matches / total_evaluated) * 100:.2f}% ({status_matches}/{total_evaluated})")
    print(f"  * Classification Accuracy       : {(classification_matches / total_evaluated) * 100:.2f}% ({classification_matches}/{total_evaluated})")
    print(f"  * Exception Detection Precision : {precision * 100:.2f}%")
    print(f"  * Exception Detection Recall    : {recall * 100:.2f}%")
    print(f"  * Exception Detection F1 Score  : {f1:.4f}")
    print(f"  * False Positives / Negatives   : {fp} / {fn}")
    print("-" * 75)

    print("[*] PART 2: ML ANOMALY DETECTION LAYER (ISOLATION FOREST)")
    total_anomalies = anom_run_res.summary.anomalies_detected
    anom_rate = anom_run_res.summary.anomaly_rate_percentage
    avg_score = anom_run_res.summary.avg_normalized_score
    print(f"  * Total Anomalies Detected      : {total_anomalies} ({anom_rate:.1f}% of population)")
    print(f"  * Mean Population Anomaly Score : {avg_score:.2f} / 100")
    print(f"  * Severity Breakdown            : {anom_run_res.summary.severity_breakdown}")
    print("-" * 75)

    print("[*] SCENARIO DUAL-ENGINE PROFILE:")
    print(f"  {'Scenario':<27} | {'Count':>5} | {'Rec Match%':>10} | {'Avg Anom Score':>14} | {'High Anom%':>10}")
    print("  " + "-" * 73)
    for st_name, m in sorted(scenario_metrics.items(), key=lambda x: -x[1]["total"]):
        stat_pct = (m["correct_status"] / m["total"]) * 100
        avg_anom = sum(m["anomaly_scores"]) / len(m["anomaly_scores"]) if m["anomaly_scores"] else 0.0
        high_pct = (m["high_anomalies"] / m["total"]) * 100
        print(f"  {st_name:<27} | {m['total']:>5} | {stat_pct:>9.1f}% | {avg_anom:>13.1f} | {high_pct:>9.1f}%")
    print("=" * 75)

    db.close()

    return {
        "total_records": total_evaluated,
        "reconciliation_accuracy": status_matches / total_evaluated,
        "classification_accuracy": classification_matches / total_evaluated,
        "anomalies_detected": total_anomalies,
        "avg_anomaly_score": avg_score,
        "rec_throughput": rec_throughput,
        "anom_throughput": anom_throughput,
    }


if __name__ == "__main__":
    run_benchmark(num_clusters=1000, seed=42)
