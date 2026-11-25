"""Seed demo carrier contract + overcharge invoice."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.audit_engine import run_audit
from app.database import Base, SessionLocal, engine
from app.models import CarrierContract, ContractRate, Invoice


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.scalar(select(Invoice).where(Invoice.invoice_number == "FLT-2024-88421"))
        if existing:
            return

        contract = CarrierContract(
            carrier_name="Continental Freight Lines",
            contract_ref="CFL-MASTER-2024",
            effective_from=date(2024, 1, 1),
            effective_to=date(2025, 12, 31),
        )
        db.add(contract)
        db.flush()

        rate = ContractRate(
            contract_id=contract.id,
            origin_city="Dallas",
            origin_state="TX",
            dest_city="Chicago",
            dest_state="IL",
            service_level="standard",
            rate_per_mile=Decimal("2.45"),
            min_charge=Decimal("425.00"),
            fuel_surcharge_pct=Decimal("12.5"),
            clause_ref="Schedule A §4.2 — Dallas–Chicago lane",
        )
        db.add(rate)

        invoice = Invoice(
            invoice_number="FLT-2024-88421",
            carrier_name="Continental Freight Lines",
            ship_date=date(2024, 6, 15),
            origin_city="Dallas",
            origin_state="TX",
            dest_city="Chicago",
            dest_state="IL",
            miles=Decimal("680"),
            billed_amount=Decimal("2150.00"),
            fuel_surcharge=Decimal("185.00"),
            status="pending",
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        run_audit(db, invoice.id)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Seed complete: contract rate + overcharge invoice FLT-2024-88421")