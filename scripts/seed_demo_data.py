import sys
import os
import argparse
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.synthetic.generator import SyntheticFinancialDataEngine
from app.synthetic.exporter import SyntheticDataExporter
from app.synthetic.seeder import DatabaseSeeder
from app.core.database import SessionLocal


def main():
    parser = argparse.ArgumentParser(description="LedgerLens Synthetic Financial Data Generator & Seeder")
    parser.add_argument("--count", type=int, default=1000, help="Number of transaction clusters to generate (default: 1000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation (default: 42)")
    parser.add_argument("--export-dir", type=str, default="data/generated", help="Directory to export CSV and JSON datasets")
    parser.add_argument("--skip-db", action="store_true", help="Skip database seeding (export files only)")

    args = parser.parse_args()

    print("=" * 65)
    print("[*] LedgerLens - Deterministic Financial Dataset Generator")
    print("=" * 65)
    print(f"* Clusters Target: {args.count:,}")
    print(f"* Random Seed:     {args.seed}")
    print(f"* Export Path:     {args.export_dir}")
    print("-" * 65)

    # 1. Generate Dataset
    engine = SyntheticFinancialDataEngine(seed=args.seed)
    dataset = engine.generate_dataset(num_clusters=args.count)

    print(f"[OK] Generated {len(dataset['orders']):,} orders across {len(dataset['merchants'])} merchants.")
    print(f"[OK] Payments captured:     {len(dataset['payments']):,}")
    print(f"[OK] Fees calculated:       {len(dataset['fees']):,}")
    print(f"[OK] Taxes (GST) computed:  {len(dataset['taxes']):,}")
    print(f"[OK] Settlements produced:  {len(dataset['settlements']):,}")
    print(f"[OK] Bank UTR records:      {len(dataset['bank_transactions']):,}")
    print(f"[OK] Ground truth labeled:  {len(dataset['ground_truth']):,}")
    print("-" * 65)

    # 2. Scenario Distribution Breakdown
    scenario_counts = {}
    for gt in dataset["ground_truth"]:
        st = gt["scenario_type"]
        scenario_counts[st] = scenario_counts.get(st, 0) + 1

    print("[*] Ground Truth Scenario Breakdown:")
    for st, cnt in sorted(scenario_counts.items(), key=lambda x: -x[1]):
        pct = (cnt / args.count) * 100
        print(f"  - {st:<28} : {cnt:>4} ({pct:>5.1f}%)")
    print("-" * 65)

    # 3. Export to JSON & CSV
    json_path = os.path.join(args.export_dir, "synthetic_dataset.json")
    SyntheticDataExporter.export_to_json(dataset, json_path)
    csv_files = SyntheticDataExporter.export_to_csv_directory(dataset, os.path.join(args.export_dir, "csv"))

    print(f"[SAVE] Exported Master JSON -> {json_path}")
    print(f"[SAVE] Exported Entity CSVs  -> {len(csv_files)} files in {os.path.join(args.export_dir, 'csv')}")

    # 4. Seed Database
    if not args.skip_db:
        print("-" * 65)
        print("[*] Seeding local database via SQLAlchemy...")
        db = SessionLocal()
        try:
            counts = DatabaseSeeder.seed(db, dataset, clear_existing=True)
            print("[OK] Database successfully seeded:")
            for entity, count in counts.items():
                print(f"  - {entity:<22} : {count:>5} records")
        finally:
            db.close()

    print("=" * 65)
    print("[DONE] LedgerLens Demo Data Ready!")
    print("=" * 65)


if __name__ == "__main__":
    main()
