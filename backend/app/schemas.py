from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    service: str


class InvoiceCreate(BaseModel):
    invoice_number: str
    carrier_name: str
    ship_date: date
    origin_city: str
    origin_state: str
    dest_city: str
    dest_state: str
    miles: Decimal
    billed_amount: Decimal
    fuel_surcharge: Decimal = Decimal("0")


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    carrier_name: str
    ship_date: date
    origin_city: str
    origin_state: str
    dest_city: str
    dest_state: str
    miles: Decimal
    billed_amount: Decimal
    fuel_surcharge: Decimal
    status: str
    uploaded_at: datetime


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_code: str
    severity: str
    title: str
    description: str
    expected_value: str
    actual_value: str
    evidence_source: str
    evidence_excerpt: str
    citation: str


class AuditRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    run_at: datetime
    expected_amount: Decimal
    variance_amount: Decimal
    verdict: str
    findings: list[FindingOut] = []


class DisputeLetterOut(BaseModel):
    audit_run_id: int
    subject: str
    body: str


class ContractRateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    origin_city: str
    origin_state: str
    dest_city: str
    dest_state: str
    rate_per_mile: Decimal
    min_charge: Decimal
    fuel_surcharge_pct: Decimal
    clause_ref: str