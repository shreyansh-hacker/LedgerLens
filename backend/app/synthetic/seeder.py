from sqlalchemy.orm import Session
from typing import Dict, Any, List
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
    """Inserts synthetic dataset into database tables via SQLAlchemy ORM with fast batched operations."""

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
        merchants = [Merchant(**m) for m in dataset.get("merchants", [])]
        if merchants:
            db.add_all(merchants)

        # 2. Orders
        orders = [Order(**o) for o in dataset.get("orders", [])]
        if orders:
            db.add_all(orders)

        # 3. Payments
        payments = [Payment(**p) for p in dataset.get("payments", [])]
        if payments:
            db.add_all(payments)

        # 4. Fees
        fees = [Fee(**f) for f in dataset.get("fees", [])]
        if fees:
            db.add_all(fees)

        # 5. Taxes
        taxes = [Tax(**t) for t in dataset.get("taxes", [])]
        if taxes:
            db.add_all(taxes)

        # 6. Refunds
        refunds = [Refund(**r) for r in dataset.get("refunds", [])]
        if refunds:
            db.add_all(refunds)

        # 7. Settlements
        settlements = [
            Settlement(
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
            )
            for s in dataset.get("settlements", [])
        ]
        if settlements:
            db.add_all(settlements)

        # 8. Bank Transactions
        bank_txns = [BankTransaction(**b) for b in dataset.get("bank_transactions", [])]
        if bank_txns:
            db.add_all(bank_txns)

        db.commit()

        return {
            "merchants": len(merchants),
            "orders": len(orders),
            "payments": len(payments),
            "fees": len(fees),
            "taxes": len(taxes),
            "refunds": len(refunds),
            "settlements": len(settlements),
            "bank_transactions": len(bank_txns),
        }
