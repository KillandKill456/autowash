from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dto.service_dto import ServiceDTO
from ..services.service_service import ServiceService

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceDTO])
def list_services(db: Session = Depends(get_db)):
    return ServiceService(db).list_all()