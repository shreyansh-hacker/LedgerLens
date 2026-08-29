from datetime import datetime
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


class DatabaseSeeder:
    """Inserts synthetic dataset into database tables using high-performance single-statement multi-row bulk execution."""

    @staticmethod
    def reset_database(db: Session) -> None:
        """Deletes all table records in strict reverse-dependency order with zero ORM session sync overhead."""
        models = [
            AuditLog,
            InvestigationResult,
            AnomalyResult,
            ReconciliationResult,
            BankTransaction,
            Settlement,
            Refund,
            Tax,
            Fee,
            Payment,
            Order,
            Merchant,
        ]
        for model in models:
            db.query(model).delete(synchronize_session=False)
        db.commit()

    @staticmethod
    def seed(db: Session, dataset: Dict[str, Any], clear_existing: bool = True) -> Dict[str, int]:
        if clear_existing:
            DatabaseSeeder.reset_database(db)

        now = datetime.utcnow()

        # 1. Merchants
        merchants = [
            {
                "id": m["id"],
                "name": m["name"],
                "email": m.get("email"),
                "currency": m.get("currency", "INR"),
                "created_at": m.get("created_at", now),
            }
            for m in dataset.get("merchants", [])
        ]
        if merchants:
            db.execute(insert(Merchant).values(merchants))

        # 2. Orders (Batch in chunks of 500 for optimal WAN packet size)
        orders = [
            {
                "id": o["id"],
                "merchant_id": o["merchant_id"],
                "order_reference": o["order_reference"],
                "customer_id": o.get("customer_id"),
                "total_amount": o["total_amount"],
                "currency": o.get("currency", "INR"),
                "status": o.get("status", "COMPLETED"),
                "created_at": o.get("created_at", now),
            }
            for o in dataset.get("orders", [])
        ]
        for i in range(0, len(orders), 500):
            chunk = orders[i:i + 500]
            if chunk:
                db.execute(insert(Order).values(chunk))

        # 3. Payments
        payments = [
            {
                "id": p["id"],
                "order_id": p["order_id"],
                "payment_reference": p["payment_reference"],
                "gateway_name": p.get("gateway_name", "Razorpay"),
                "amount": p["amount"],
                "currency": p.get("currency", "INR"),
                "method": p.get("method", "UPI"),
                "status": p.get("status", "captured"),
                "captured_at": p.get("captured_at", now),
            }
            for p in dataset.get("payments", [])
        ]
        for i in range(0, len(payments), 500):
            chunk = payments[i:i + 500]
            if chunk:
                db.execute(insert(Payment).values(chunk))

        # 4. Fees
        fees = [
            {
                "id": f["id"],
                "payment_id": f["payment_id"],
                "fee_type": f.get("fee_type", "gateway_fee"),
                "rate_percentage": f.get("rate_percentage"),
                "amount": f["amount"],
                "currency": f.get("currency", "INR"),
                "created_at": f.get("created_at", now),
            }
            for f in dataset.get("fees", [])
        ]
        for i in range(0, len(fees), 500):
            chunk = fees[i:i + 500]
            if chunk:
                db.execute(insert(Fee).values(chunk))

        # 5. Taxes
        taxes = [
            {
                "id": t["id"],
                "payment_id": t["payment_id"],
                "tax_type": t.get("tax_type", "GST_18"),
                "rate_percentage": t.get("rate_percentage", 18.00),
                "amount": t["amount"],
                "currency": t.get("currency", "INR"),
                "created_at": t.get("created_at", now),
            }
            for t in dataset.get("taxes", [])
        ]
        for i in range(0, len(taxes), 500):
            chunk = taxes[i:i + 500]
            if chunk:
                db.execute(insert(Tax).values(chunk))

        # 6. Refunds
        refunds = [
            {
                "id": r["id"],
                "payment_id": r["payment_id"],
                "refund_reference": r["refund_reference"],
                "amount": r["amount"],
                "reason": r.get("reason"),
                "status": r.get("status", "processed"),
                "created_at": r.get("created_at", now),
            }
            for r in dataset.get("refunds", [])
        ]
        for i in range(0, len(refunds), 500):
            chunk = refunds[i:i + 500]
            if chunk:
                db.execute(insert(Refund).values(chunk))

        # 7. Settlements
        valid_pay_ids = {p["id"] for p in payments}
        settlements = [
            {
                "id": s["id"],
                "payment_id": s["payment_id"] if s.get("payment_id") in valid_pay_ids else None,
                "settlement_reference": s["settlement_reference"],
                "gross_amount": s["gross_amount"],
                "fee_amount": s.get("fee_amount", 0.00),
                "tax_amount": s.get("tax_amount", 0.00),
                "net_amount": s["net_amount"],
                "currency": s.get("currency", "INR"),
                "status": s.get("status", "settled"),
                "settled_at": s.get("settled_at", now),
            }
            for s in dataset.get("settlements", [])
        ]
        for i in range(0, len(settlements), 500):
            chunk = settlements[i:i + 500]
            if chunk:
                db.execute(insert(Settlement).values(chunk))

        # 8. Bank Transactions
        valid_set_ids = {s["id"] for s in settlements}
        bank_txns = [
            {
                "id": b["id"],
                "settlement_id": b["settlement_id"] if b.get("settlement_id") in valid_set_ids else None,
                "bank_reference": b["bank_reference"],
                "account_number_mask": b.get("account_number_mask", "XX1234"),
                "credit_amount": b["credit_amount"],
                "currency": b.get("currency", "INR"),
                "utr_number": b.get("utr_number"),
                "transaction_date": b.get("transaction_date", b.get("credited_at", now)),
            }
            for b in dataset.get("bank_transactions", [])
        ]
        for i in range(0, len(bank_txns), 500):
            chunk = bank_txns[i:i + 500]
            if chunk:
                db.execute(insert(BankTransaction).values(chunk))

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
