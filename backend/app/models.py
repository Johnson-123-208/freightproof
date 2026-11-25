from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CarrierContract(Base):
    __tablename__ = "carrier_contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    carrier_name: Mapped[str] = mapped_column(String(120))
    contract_ref: Mapped[str] = mapped_column(String(64), unique=True)
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rates: Mapped[list["ContractRate"]] = relationship(back_populates="contract")


class ContractRate(Base):
    __tablename__ = "contract_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("carrier_contracts.id"))
    origin_city: Mapped[str] = mapped_column(String(80))
    origin_state: Mapped[str] = mapped_column(String(2))
    dest_city: Mapped[str] = mapped_column(String(80))
    dest_state: Mapped[str] = mapped_column(String(2))
    service_level: Mapped[str] = mapped_column(String(32), default="standard")
    rate_per_mile: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    min_charge: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fuel_surcharge_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    clause_ref: Mapped[str] = mapped_column(String(64))

    contract: Mapped["CarrierContract"] = relationship(back_populates="rates")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(64), unique=True)
    carrier_name: Mapped[str] = mapped_column(String(120))
    ship_date: Mapped[date] = mapped_column(Date)
    origin_city: Mapped[str] = mapped_column(String(80))
    origin_state: Mapped[str] = mapped_column(String(2))
    dest_city: Mapped[str] = mapped_column(String(80))
    dest_state: Mapped[str] = mapped_column(String(2))
    miles: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    billed_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fuel_surcharge: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    audit_runs: Mapped[list["AuditRun"]] = relationship(back_populates="invoice")


class AuditRun(Base):
    __tablename__ = "audit_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    run_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    variance_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    verdict: Mapped[str] = mapped_column(String(32))

    invoice: Mapped["Invoice"] = relationship(back_populates="audit_runs")
    findings: Mapped[list["AuditFinding"]] = relationship(back_populates="audit_run")


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    audit_run_id: Mapped[int] = mapped_column(ForeignKey("audit_runs.id"))
    rule_code: Mapped[str] = mapped_column(String(32))
    severity: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    expected_value: Mapped[str] = mapped_column(String(64))
    actual_value: Mapped[str] = mapped_column(String(64))
    evidence_source: Mapped[str] = mapped_column(String(120))
    evidence_excerpt: Mapped[str] = mapped_column(Text)
    citation: Mapped[str] = mapped_column(String(120))

    audit_run: Mapped["AuditRun"] = relationship(back_populates="findings")


class DisputeLetter(Base):
    __tablename__ = "dispute_letters"

    id: Mapped[int] = mapped_column(primary_key=True)
    audit_run_id: Mapped[int] = mapped_column(ForeignKey("audit_runs.id"), unique=True)
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)