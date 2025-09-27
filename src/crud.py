# src/crud.py
from src.adapters.repositories.device_repository import SQLAlchemyDeviceRepository
from src.adapters.repositories.models import Microcontroller, UserMicrocontroller, Plant
from sqlalchemy.orm import Session
from uuid import UUID

ROLE_LEVEL = {"viewer": 0, "editor": 1, "owner": 2}

def user_has_permission(db: Session, user_id: str, device_id: str, min_role="viewer") -> bool:
    assoc = db.query(UserMicrocontroller).filter_by(user_id=user_id, microcontroller_id=device_id).first()
    if not assoc:
        return False
    return ROLE_LEVEL.get(assoc.role, 0) >= ROLE_LEVEL.get(min_role, 0)
