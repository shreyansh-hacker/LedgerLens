import datetime
from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Boolean,
    Enum as SQLEnum,
    Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ReconciliationStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    EXCEPTION = "EXCEPTION"
    MISSING_SETTLEMENT = "MISSING_SETTLEMENT"
    MISSING_BANK_TRANSACTION = "MISSING_BANK_TRANSACTION"
    DUPLICATE = "DUPLICATE"
    REVIEW = "REVIEW"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class InvestigationStatus(str, enum.Enum):
    EXPLAINED = "EXPLAINED"
    PARTIALLY_EXPLAINED = "PARTIALLY_EXPLAINED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    MANUALLY_OVERRIDDEN = "MANUALLY_OVERRIDDEN"
    UNRESOLVED = "UNRESOLVED"


class AnomalySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    currency = Column(String(3), default="INR", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(64), primary_key=True, index=True)
    merchant_id = Column(String(64), ForeignKey("merchants.id"), nullable=False, index=True)
    order_reference = Column(String(128), unique=True, index=True, nullable=False)
    customer_id = Column(String(128), nullable=True)
    total_amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(32), default="COMPLETED", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    payments = relationship("Payment", back_populates="order")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(64), primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.id"), nullable=False, index=True)
    payment_reference = Column(String(128), unique=True, index=True, nullable=False)
    gateway_name = Column(String(64), default="Razorpay", nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    method = Column(String(32), default="UPI", nullable=False)
    status = Column(String(32), default="captured", nullable=False)
    captured_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    order = relationship("Order", back_populates="payments")
    fees = relationship("Fee", back_populates="payment")
    taxes = relationship("Tax", back_populates="payment")
    refunds = relationship("Refund", back_populates="payment")
    settlement = relationship("Settlement", back_populates="payment", uselist=False)


class Fee(Base):
    __tablename__ = "fees"

    id = Column(String(64), primary_key=True, index=True)
    payment_id = Column(String(64), ForeignKey("payments.id"), nullable=False, index=True)
    fee_type = Column(String(64), default="gateway_fee", nullable=False)
    rate_percentage = Column(Numeric(6, 4), nullable=True)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    payment = relationship("Payment", back_populates="fees")


class Tax(Base):
    __tablename__ = "taxes"

    id = Column(String(64), primary_key=True, index=True)
    payment_id = Column(String(64), ForeignKey("payments.id"), nullable=False, index=True)
    tax_type = Column(String(64), default="GST_18", nullable=False)
    rate_percentage = Column(Numeric(6, 4), default=18.00, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    payment = relationship("Payment", back_populates="taxes")


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String(64), primary_key=True, index=True)
    payment_id = Column(String(64), ForeignKey("payments.id"), nullable=False, index=True)
    refund_reference = Column(String(128), unique=True, index=True, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    reason = Column(String(255), nullable=True)
    status = Column(String(32), default="processed", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    payment = relationship("Payment", back_populates="refunds")


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(String(64), primary_key=True, index=True)
    payment_id = Column(String(64), ForeignKey("payments.id"), nullable=True, index=True)
    settlement_reference = Column(String(128), unique=True, index=True, nullable=False)
    gross_amount = Column(Numeric(14, 2), nullable=False)
    fee_amount = Column(Numeric(14, 2), default=0.00, nullable=False)
    tax_amount = Column(Numeric(14, 2), default=0.00, nullable=False)
    net_amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(32), default="settled", nullable=False)
    settled_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    payment = relationship("Payment", back_populates="settlement")
    bank_transaction = relationship("BankTransaction", back_populates="settlement", uselist=False)


class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id = Column(String(64), primary_key=True, index=True)
    settlement_id = Column(String(64), ForeignKey("settlements.id"), nullable=True, index=True)
    bank_reference = Column(String(128), unique=True, index=True, nullable=False)
    account_number_mask = Column(String(32), default="XX1234", nullable=False)
    credit_amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    utr_number = Column(String(64), nullable=True, index=True)
    transaction_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    settlement = relationship("Settlement", back_populates="bank_transaction")


class ReconciliationResult(Base):
    __tablename__ = "reconciliation_results"

    id = Column(String(64), primary_key=True, index=True)
    payment_id = Column(String(64), ForeignKey("payments.id"), nullable=False, index=True)
    order_id = Column(String(64), ForeignKey("orders.id"), nullable=True, index=True)
    settlement_id = Column(String(64), ForeignKey("settlements.id"), nullable=True, index=True)
    bank_transaction_id = Column(String(64), ForeignKey("bank_transactions.id"), nullable=True, index=True)

    expected_settlement_amount = Column(Numeric(14, 2), nullable=False)
    actual_settlement_amount = Column(Numeric(14, 2), nullable=True)
    expected_bank_amount = Column(Numeric(14, 2), nullable=False)
    actual_bank_amount = Column(Numeric(14, 2), nullable=True)
    discrepancy_amount = Column(Numeric(14, 2), default=0.00, nullable=False)

    matching_score = Column(Numeric(5, 2), nullable=False)  # 0 to 100
    matching_method = Column(String(64), default="EXACT_REFERENCE", nullable=False)  # EXACT_REFERENCE, DIRECT_ID_LINK, AMOUNT_PROXIMITY, UNMATCHED
    status = Column(SQLEnum(ReconciliationStatus), default=ReconciliationStatus.MATCHED, nullable=False, index=True)
    classification = Column(String(64), default="NONE", nullable=False, index=True)  # NONE, FEE_MISMATCH, TAX_MISMATCH, MISSING_BANK_TRANSACTION, MISSING_SETTLEMENT, DUPLICATE_SETTLEMENT, REFERENCE_ID_DISCREPANCY, AMOUNT_MISMATCH, SETTLEMENT_DELAY, UNEXPLAINED_EXCEPTION
    operational_warning = Column(String(64), nullable=True)  # e.g., SETTLEMENT_DELAY
    ground_truth_scenario = Column(String(64), nullable=True)  # Populated only during evaluation benchmark runs

    evidence_payload = Column(JSON, nullable=True)
    reconciled_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    investigation = relationship("InvestigationResult", back_populates="reconciliation_result", uselist=False)
    anomaly = relationship("AnomalyResult", back_populates="reconciliation_result", uselist=False)


class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(String(64), primary_key=True, index=True)
    reconciliation_id = Column(String(64), ForeignKey("reconciliation_results.id"), nullable=False, index=True)
    
    is_anomaly = Column(Boolean, default=False, nullable=False, index=True)
    raw_anomaly_score = Column(Numeric(8, 5), nullable=False)
    normalized_score = Column(Numeric(5, 2), nullable=False, index=True)  # 0 to 100
    severity = Column(SQLEnum(AnomalySeverity), default=AnomalySeverity.LOW, nullable=False, index=True)
    detected_features = Column(JSON, nullable=True)
    explanation_signals = Column(JSON, nullable=True)
    model_version = Column(String(64), default="isolation_forest_v1.0", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    reconciliation_result = relationship("ReconciliationResult", back_populates="anomaly")


class InvestigationResult(Base):
    __tablename__ = "investigation_results"

    id = Column(String(64), primary_key=True, index=True)
    reconciliation_id = Column(String(64), ForeignKey("reconciliation_results.id"), nullable=False, index=True)
    evidence_hash = Column(String(64), nullable=False, index=True)
    
    investigation_status = Column(SQLEnum(InvestigationStatus), default=InvestigationStatus.EXPLAINED, nullable=False, index=True)
    summary = Column(Text, nullable=False)
    facts = Column(JSON, nullable=False)  # List of {statement: str, evidence_ids: List[str]}
    explanation = Column(Text, nullable=False)
    evidence_references = Column(JSON, nullable=True)
    missing_evidence = Column(JSON, nullable=True)
    
    ai_confidence = Column(Numeric(5, 2), nullable=False)  # 0 to 100
    system_confidence = Column(Numeric(5, 2), nullable=False)  # composite 0 to 100
    confidence_tier = Column(String(16), default="HIGH", nullable=False)  # HIGH, MEDIUM, LOW
    
    recommended_action = Column(String(255), nullable=False)
    human_override = Column(Boolean, default=False, nullable=False)
    reviewer_note = Column(Text, nullable=True)
    cached = Column(Boolean, default=False, nullable=False)
    latency_ms = Column(Numeric(8, 2), default=0.00, nullable=False)
    model_name = Column(String(64), default="llama-3.3-70b-versatile", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    reconciliation_result = relationship("ReconciliationResult", back_populates="investigation")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True)
    entity_type = Column(String(64), nullable=False, index=True)  # RECONCILIATION, INVESTIGATION, OVERRIDE
    entity_id = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    actor = Column(String(64), default="SYSTEM", nullable=False)
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)


# Compound indexes for fast lookups
Index("idx_orders_merchant_created", Order.merchant_id, Order.created_at)
Index("idx_payments_order_captured", Payment.order_id, Payment.captured_at)
Index("idx_reconciliation_status_discrepancy", ReconciliationResult.status, ReconciliationResult.discrepancy_amount)
Index("idx_reconciliation_classification", ReconciliationResult.classification)
Index("idx_anomaly_severity_score", AnomalyResult.severity, AnomalyResult.normalized_score)
Index("idx_investigation_status_hash", InvestigationResult.investigation_status, InvestigationResult.evidence_hash)
