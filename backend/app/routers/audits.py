from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.audit_engine import draft_dispute_letter
from app.database import get_db
from app.models import AuditRun, DisputeLetter
from app.schemas import AuditRunOut, DisputeLetterOut

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("/{audit_run_id}", response_model=AuditRunOut)
def get_audit(audit_run_id: int, db: Session = Depends(get_db)) -> AuditRun:
    run = (
        db.scalars(
            select(AuditRun)
            .where(AuditRun.id == audit_run_id)
            .options(joinedload(AuditRun.findings))
        )
        .unique()
        .first()
    )
    if not run:
        raise HTTPException(404, "Audit run not found")
    return run


@router.post("/{audit_run_id}/dispute-letter", response_model=DisputeLetterOut)
def generate_dispute(audit_run_id: int, db: Session = Depends(get_db)) -> DisputeLetterOut:
    run = db.get(AuditRun, audit_run_id)
    if not run:
        raise HTTPException(404, "Audit run not found")
    invoice = run.invoice
    try:
        body = draft_dispute_letter(db, audit_run_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e

    subject = f"Dispute — Invoice {invoice.invoice_number} ({run.variance_amount} variance)"
    existing = db.scalar(select(DisputeLetter).where(DisputeLetter.audit_run_id == audit_run_id))
    if existing:
        existing.subject = subject
        existing.body = body
    else:
        db.add(DisputeLetter(audit_run_id=audit_run_id, subject=subject, body=body))
    db.commit()

    return DisputeLetterOut(audit_run_id=audit_run_id, subject=subject, body=body)