from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CarrierContract, ContractRate
from app.schemas import ContractRateOut

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("/rates", response_model=list[ContractRateOut])
def list_rates(db: Session = Depends(get_db)) -> list[ContractRate]:
    stmt = (
        select(ContractRate)
        .join(CarrierContract)
        .order_by(CarrierContract.carrier_name, ContractRate.origin_city)
    )
    return list(db.scalars(stmt).all())