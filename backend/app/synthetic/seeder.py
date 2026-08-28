from sqlalchemy.orm import Session
from typing import Dict, Any
from app.models.schema import (
    Merchant,
    Order,
    Payment,
    Fee,
    Tax,
    Refund,
    Settlement,
    BankTransaction,
    ReconciliationResult,
    AnomalyResult,
    InvestigationResult,
    AuditLog,
)
from app.core.database import Base, engine


class DatabaseSeeder:
    """Inserts synthetic dataset into database tables via SQLAlchemy ORM."""

    @staticmethod
    def reset_database(db: Session) -> None:
        """Deletes all table records in strict reverse-dependency order."""
        Base.metadata.create_all(bind=engine)
        db.query(AuditLog).delete()
        db.query(InvestigationResult).delete()
        db.query(AnomalyResult).delete()
        db.query(ReconciliationResult).delete()
        db.query(BankTransaction).delete()
        db.query(Settlement).delete()
        db.query(Refund).delete()
        db.query(Tax).delete()
        db.query(Fee).delete()
        db.query(Payment).delete()
        db.query(Order).delete()
        db.query(Merchant).delete()
        db.commit()

    @staticmethod
    def seed(db: Session, dataset: Dict[str, Any], clear_existing: bool = True) -> Dict[str, int]:
        # Ensure schema tables exist
        Base.metadata.create_all(bind=engine)

        if clear_existing:
            DatabaseSeeder.reset_database(db)

        # 1. Merchants
        for m in dataset.get("merchants", []):
            db.add(Merchant(**m))
        db.commit()

        # 2. Orders
        for o in dataset.get("orders", []):
            db.add(Order(**o))
        db.commit()

        # 3. Payments
        for p in dataset.get("payments", []):
            db.add(Payment(**p))
        db.commit()

        # 4. Fees
        for f in dataset.get("fees", []):
            db.add(Fee(**f))
        db.commit()

        # 5. Taxes
        for t in dataset.get("taxes", []):
            db.add(Tax(**t))
        db.commit()

        # 6. Refunds
        for r in dataset.get("refunds", []):
            db.add(Refund(**r))
        db.commit()

        # 7. Settlements
        for s in dataset.get("settlements", []):
            db.add(Settlement(
                id=s["id"],
                payment_id=s["payment_id"] if not s["payment_id"].startswith("pay_unknown") else None,
                settlement_reference=s["settlement_reference"],
                gross_amount=s["gross_amount"],
                fee_amount=s["fee_amount"],
                tax_amount=s["tax_amount"],
                net_amount=s["net_amount"],
                currency=s["currency"],
                status=s["status"],
                settled_at=s["settled_at"],
            ))
        db.commit()

        # 8. Bank Transactions
        for b in dataset.get("bank_transactions", []):
            db.add(BankTransaction(**b))
        db.commit()

        return {
            "merchants": len(dataset.get("merchants", [])),
            "orders": len(dataset.get("orders", [])),
            "payments": len(dataset.get("payments", [])),
            "fees": len(dataset.get("fees", [])),
            "taxes": len(dataset.get("taxes", [])),
            "refunds": len(dataset.get("refunds", [])),
            "settlements": len(dataset.get("settlements", [])),
            "bank_transactions": len(dataset.get("bank_transactions", [])),
            "ground_truth_records": len(dataset.get("ground_truth", [])),
        }
