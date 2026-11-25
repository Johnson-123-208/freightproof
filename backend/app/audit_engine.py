"""Deterministic freight invoice audit — no LLM for monetary calculations."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditFinding, AuditRun, CarrierContract, ContractRate, Invoice


MONEY = Decimal("0.01")


@dataclass(frozen=True)
class RateMatch:
    rate: ContractRate
    contract: CarrierContract


def _quantize(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY, rounding=ROUND_HALF_UP)


def find_contract_rate(
    db: Session,
    invoice: Invoice,
    carrier_name: str,
) -> RateMatch | None:
    stmt = (
        select(ContractRate, CarrierContract)
        .join(CarrierContract, ContractRate.contract_id == CarrierContract.id)
        .where(CarrierContract.carrier_name == carrier_name)
        .where(ContractRate.origin_city == invoice.origin_city)
        .where(ContractRate.origin_state == invoice.origin_state)
        .where(ContractRate.dest_city == invoice.dest_city)
        .where(ContractRate.dest_state == invoice.dest_state)
        .where(CarrierContract.effective_from <= invoice.ship_date)
    )
    rows = db.execute(stmt).all()
    for rate, contract in rows:
        if contract.effective_to is None or contract.effective_to >= invoice.ship_date:
            return RateMatch(rate=rate, contract=contract)
    return None


def compute_expected_charge(match: RateMatch, miles: Decimal, fuel_billed: Decimal) -> tuple[Decimal, list[dict]]:
    """Returns (expected_total, line_items_for_evidence)."""
    rate = match.rate
    linehaul = _quantize(miles * rate.rate_per_mile)
    if linehaul < rate.min_charge:
        linehaul = _quantize(rate.min_charge)
    fuel = _quantize(linehaul * (rate.fuel_surcharge_pct / Decimal("100")))
    total = _quantize(linehaul + fuel)
    items = [
        {
            "label": "Linehaul",
            "formula": f"{miles} mi × ${rate.rate_per_mile}/mi (min ${rate.min_charge})",
            "amount": str(linehaul),
        },
        {
            "label": "Contract fuel surcharge",
            "formula": f"{rate.fuel_surcharge_pct}% of linehaul",
            "amount": str(fuel),
        },
        {
            "label": "Invoice fuel surcharge (billed)",
            "formula": "from invoice",
            "amount": str(fuel_billed),
        },
    ]
    return total, items


def run_audit(db: Session, invoice_id: int) -> AuditRun:
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise ValueError("Invoice not found")

    match = find_contract_rate(db, invoice, invoice.carrier_name)
    findings_data: list[dict] = []

    if not match:
        expected = Decimal("0")
        variance = invoice.billed_amount
        verdict = "no_contract"
        findings_data.append(
            {
                "rule_code": "NO_RATE",
                "severity": "warning",
                "title": "No matching contract rate",
                "description": "No active contract rate found for this lane and ship date.",
                "expected_value": "—",
                "actual_value": f"${invoice.billed_amount}",
                "evidence_source": "Rate table",
                "evidence_excerpt": f"Lane: {invoice.origin_city}, {invoice.origin_state} → "
                f"{invoice.dest_city}, {invoice.dest_state} on {invoice.ship_date}",
                "citation": "Internal rate master",
            }
        )
    else:
        expected, calc_items = compute_expected_charge(match, invoice.miles, invoice.fuel_surcharge)
        variance = _quantize(invoice.billed_amount - expected)
        if variance > Decimal("0"):
            verdict = "overcharge"
        elif variance < Decimal("0"):
            verdict = "undercharge"
        else:
            verdict = "matched"

        calc_text = "; ".join(f"{i['label']}: {i['amount']} ({i['formula']})" for i in calc_items)
        findings_data.append(
            {
                "rule_code": "RATE_VERIFY",
                "severity": "critical" if variance > Decimal("0") else "info",
                "title": "Linehaul and fuel vs contract",
                "description": (
                    f"Deterministic recalculation from contract {match.contract.contract_ref} "
                    f"clause {match.rate.clause_ref}."
                ),
                "expected_value": f"${expected}",
                "actual_value": f"${invoice.billed_amount}",
                "evidence_source": f"Contract {match.contract.contract_ref}",
                "evidence_excerpt": calc_text,
                "citation": match.rate.clause_ref,
            }
        )
        if variance > Decimal("0"):
            findings_data.append(
                {
                    "rule_code": "OVERCHARGE",
                    "severity": "critical",
                    "title": "Overcharge detected",
                    "description": (
                        f"Billed amount exceeds contract expectation by ${variance} "
                        f"(deterministic arithmetic only)."
                    ),
                    "expected_value": f"${expected}",
                    "actual_value": f"${invoice.billed_amount}",
                    "evidence_source": invoice.invoice_number,
                    "evidence_excerpt": (
                        f"Invoice {invoice.invoice_number} total ${invoice.billed_amount}; "
                        f"contract expectation ${expected}."
                    ),
                    "citation": match.rate.clause_ref,
                }
            )

        if invoice.fuel_surcharge > Decimal("0") and match.rate.fuel_surcharge_pct == Decimal("0"):
            findings_data.append(
                {
                    "rule_code": "FUEL_SURCHARGE",
                    "severity": "medium",
                    "title": "Unexpected fuel surcharge line",
                    "description": "Invoice includes fuel surcharge; verify against current FSC index.",
                    "expected_value": "$0.00",
                    "actual_value": f"${invoice.fuel_surcharge}",
                    "evidence_source": invoice.invoice_number,
                    "evidence_excerpt": f"Fuel line on invoice: ${invoice.fuel_surcharge}",
                    "citation": "Carrier tariff § FSC",
                }
            )

    run = AuditRun(
        invoice_id=invoice.id,
        expected_amount=expected if match else Decimal("0"),
        variance_amount=variance,
        verdict=verdict,
    )
    db.add(run)
    db.flush()

    for f in findings_data:
        db.add(AuditFinding(audit_run_id=run.id, **f))

    invoice.status = "audited"
    db.commit()
    db.refresh(run)
    return run


def draft_dispute_letter(db: Session, audit_run_id: int) -> str:
    run = db.get(AuditRun, audit_run_id)
    if not run:
        raise ValueError("Audit run not found")
    invoice = run.invoice
    findings = run.findings
    overcharge = next((f for f in findings if f.rule_code == "OVERCHARGE"), None)
    rate_finding = next((f for f in findings if f.rule_code == "RATE_VERIFY"), None)

    citation = rate_finding.citation if rate_finding else "contract rate schedule"
    body = f"""Dear {invoice.carrier_name} Accounts Payable,

We are disputing invoice {invoice.invoice_number} dated {invoice.ship_date} for shipment
{invoice.origin_city}, {invoice.origin_state} to {invoice.dest_city}, {invoice.dest_state}.

Per our contracted rate ({citation}), the auditable charge should be {run.expected_amount}.
Your invoice reflects {invoice.billed_amount}, a variance of {run.variance_amount}.

Evidence:
"""
    for f in findings:
        body += f"\n• {f.title}: {f.evidence_excerpt} [{f.citation}]\n"

    if overcharge:
        body += f"""
We request a credit of {run.variance_amount} and a corrected invoice.

Sincerely,
Accounts Payable — Demo Org
"""
    else:
        body += "\nPlease review and confirm alignment with our contract.\n\nSincerely,\nAccounts Payable — Demo Org\n"

    return body.strip()