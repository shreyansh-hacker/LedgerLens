from sqlalchemy.orm import Session
from sqlalchemy import insert
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
    """Inserts synthetic dataset into database tables using high-performance multi-row bulk execution."""

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
        merchants = dataset.get("merchants", [])
        if merchants:
            db.execute(insert(Merchant), merchants)

        # 2. Orders
        orders = dataset.get("orders", [])
        if orders:
            db.execute(insert(Order), orders)

        # 3. Payments
        payments = dataset.get("payments", [])
        if payments:
            db.execute(insert(Payment), payments)

        # 4. Fees
        fees = dataset.get("fees", [])
        if fees:
            db.execute(insert(Fee), fees)

        # 5. Taxes
        taxes = dataset.get("taxes", [])
        if taxes:
            db.execute(insert(Tax), taxes)

        # 6. Refunds
        refunds = dataset.get("refunds", [])
        if refunds:
            db.execute(insert(Refund), refunds)

        # 7. Settlements
        settlements = [
            {
                "id": s["id"],
                "payment_id": s["payment_id"] if not s["payment_id"].startswith("pay_unknown") else None,
                "settlement_reference": s["settlement_reference"],
                "gross_amount": s["gross_amount"],
                "fee_amount": s["fee_amount"],
                "tax_amount": s["tax_amount"],
                "net_amount": s["net_amount"],
                "currency": s["currency"],
                "status": s["status"],
                "settled_at": s["settled_at"],
            }
            for s in dataset.get("settlements", [])
        ]
        if settlements:
            db.execute(insert(Settlement), settlements)

        # 8. Bank Transactions
        bank_txns = dataset.get("bank_transactions", [])
        if bank_txns:
            db.execute(insert(BankTransaction), bank_txns)

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
