from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.audit_engine import run_audit
from app.database import get_db
from app.models import AuditRun, Invoice
from app.schemas import AuditRunOut, InvoiceCreate, InvoiceOut

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db)) -> list[Invoice]:
    return list(db.scalars(select(Invoice).order_by(Invoice.uploaded_at.desc())).all())


@router.post("", response_model=InvoiceOut, status_code=201)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)) -> Invoice:
    inv = Invoice(**payload.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)) -> Invoice:
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    return inv


@router.post("/{invoice_id}/audit", response_model=AuditRunOut)
def audit_invoice(invoice_id: int, db: Session = Depends(get_db)) -> AuditRun:
    try:
        run = run_audit(db, invoice_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e
    return (
        db.scalars(
            select(AuditRun)
            .where(AuditRun.id == run.id)
            .options(joinedload(AuditRun.findings))
        )
        .unique()
        .one()
    )


@router.get("/{invoice_id}/audits", response_model=list[AuditRunOut])
def list_audits(invoice_id: int, db: Session = Depends(get_db)) -> list[AuditRun]:
    return list(
        db.scalars(
            select(AuditRun)
            .where(AuditRun.invoice_id == invoice_id)
            .options(joinedload(AuditRun.findings))
            .order_by(AuditRun.run_at.desc())
        )
        .unique()
        .all()
    )