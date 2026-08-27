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
from app.models.schema import ReconciliationResult, ReconciliationStatus


def run_benchmark(num_clusters: int = 1000, seed: int = 42) -> Dict[str, Any]:
    print("=" * 70)
    print("[*] LedgerLens - Deterministic Reconciliation Benchmark")
    print("=" * 70)
    print(f"* Benchmark Dataset Scale : {num_clusters:,} clusters")
    print(f"* Deterministic PRNG Seed : {seed}")
    print("-" * 70)

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

    # Seed financial records (hidden ground truth remains outside the DB)
    DatabaseSeeder.seed(db, dataset, clear_existing=True)

    # 3. Run Deterministic Reconciliation Engine
    t1 = time.perf_counter()
    rec_engine = DeterministicReconciliationEngine()
    run_res = rec_engine.reconcile_all(db=db, clear_existing=True)
    rec_time = time.perf_counter() - t1

    throughput = num_clusters / rec_time if rec_time > 0 else 0.0
    print(f"[OK] Reconciled {num_clusters:,} records in {rec_time:.3f}s ({throughput:,.1f} records/sec)")
    print("-" * 70)

    # 4. Compare Reconciliation Results with Hidden Ground Truth
    reconciled_results: List[ReconciliationResult] = db.query(ReconciliationResult).order_by(ReconciliationResult.payment_id).all()
    ground_truth_list = dataset["ground_truth"]

    gt_by_cluster_idx = {}
    for gt in ground_truth_list:
        idx = int(gt["cluster_id"].replace("CLU_", ""))
        gt_by_cluster_idx[idx] = gt

    total_evaluated = len(reconciled_results)
    status_matches = 0
    classification_matches = 0
    amount_discrepancy_exact_matches = 0

    tp = 0  # True Positive: GT is exception, Engine flagged exception/missing/duplicate
    fp = 0  # False Positive: GT is normal/matched, Engine flagged exception
    tn = 0  # True Negative: GT is normal, Engine flagged matched
    fn = 0  # False Negative: GT is exception, Engine flagged matched

    scenario_metrics: Dict[str, Dict[str, int]] = {}

    for r in reconciled_results:
        idx = int(r.payment_id.replace("pay_", ""))
        gt = gt_by_cluster_idx[idx]
        st_type = gt["scenario_type"]

        st_key = st_type.value if hasattr(st_type, "value") else str(st_type)
        scenario_metrics.setdefault(st_key, {"total": 0, "correct_status": 0, "correct_class": 0})
        scenario_metrics[st_key]["total"] += 1

        is_gt_exception = (gt["expected_status"] != "MATCHED")
        is_engine_exception = (r.status != ReconciliationStatus.MATCHED)

        # Evaluate Status Match
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

        # Evaluate Classification Match
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

        # Evaluate Discrepancy Amount Exact Match
        gt_diff = Decimal(str(gt["expected_difference"]))
        if abs(r.discrepancy_amount) == abs(gt_diff) or (st_key in ["REFERENCE_ID_DISCREPANCY", "SETTLEMENT_DELAY"] and r.discrepancy_amount == Decimal("0.00")):
            amount_discrepancy_exact_matches += 1

        # Binary Confusion Matrix for Exception Detection
        if is_gt_exception and is_engine_exception:
            tp += 1
        elif not is_gt_exception and not is_engine_exception:
            tn += 1
        elif not is_gt_exception and is_engine_exception:
            fp += 1
        elif is_gt_exception and not is_engine_exception:
            fn += 1

    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 1.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 1.0
    accuracy = (tp + tn) / total_evaluated

    print("[*] BENCHMARK EVALUATION RESULTS:")
    print(f"  * Overall Status Accuracy         : {(status_matches / total_evaluated) * 100:.2f}% ({status_matches}/{total_evaluated})")
    print(f"  * Classification Accuracy         : {(classification_matches / total_evaluated) * 100:.2f}% ({classification_matches}/{total_evaluated})")
    print(f"  * Discrepancy Amount Accuracy     : {(amount_discrepancy_exact_matches / total_evaluated) * 100:.2f}%")
    print(f"  * Exception Detection Precision   : {precision * 100:.2f}%")
    print(f"  * Exception Detection Recall      : {recall * 100:.2f}%")
    print(f"  * Exception Detection F1 Score    : {f1:.4f}")
    print(f"  * False Positives                 : {fp}")
    print(f"  * False Negatives                 : {fn}")
    print("-" * 70)
    print("[*] SCENARIO-BY-SCENARIO ACCURACY:")
    print(f"  {'Scenario':<28} | {'Total':>5} | {'Status %':>9} | {'Class %':>9}")
    print("  " + "-" * 62)
    for st_name, counts in sorted(scenario_metrics.items(), key=lambda x: -x[1]["total"]):
        stat_pct = (counts["correct_status"] / counts["total"]) * 100
        cls_pct = (counts["correct_class"] / counts["total"]) * 100
        print(f"  {st_name:<28} | {counts['total']:>5} | {stat_pct:>8.1f}% | {cls_pct:>8.1f}%")
    print("=" * 70)

    db.close()

    return {
        "total_records": total_evaluated,
        "status_accuracy": status_matches / total_evaluated,
        "classification_accuracy": classification_matches / total_evaluated,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positives": fp,
        "false_negatives": fn,
        "throughput_records_per_sec": throughput,
    }


if __name__ == "__main__":
    run_benchmark(num_clusters=1000, seed=42)
