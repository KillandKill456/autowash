from sqlalchemy import select
from sqlalchemy.orm import Session

from ..dto.service_dto import ServiceDTO
from ..models import Service


class ServiceService:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[ServiceDTO]:
        rows = self.db.execute(select(Service)).scalars().all()
        return [ServiceDTO.model_validate(r) for r in rows]