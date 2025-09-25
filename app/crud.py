# app/crud.py 
from sqlalchemy.orm import Session
from . import models

ROLE_LEVEL = {"viewer": 0, "editor": 1, "owner": 2}

def get_user_association(db: Session, user_id: str, device_id: str):
    return db.query(models.UserMicrocontroller).filter_by(user_id=user_id, microcontroller_id=device_id).first()

def user_has_permission(db: Session, user_id: str, device_id: str, min_role="viewer", allow_admin_claims=None, user_claims=None):
    # allow_admin_claims: if user has 'admin' in the JWT we allow
    if user_claims and "admin" in user_claims:
        return True
    assoc = get_user_association(db, user_id, device_id)
    if not assoc:
        return False
    return ROLE_LEVEL.get(assoc.role, 0) >= ROLE_LEVEL.get(min_role, 0)

def list_devices_for_user(db: Session, user_id: str, filters: dict):
    q = db.query(models.Microcontroller, models.UserMicrocontroller.role, models.Plant).join(
        models.UserMicrocontroller, models.UserMicrocontroller.microcontroller_id == models.Microcontroller.id
    ).outerjoin(models.Plant, models.Microcontroller.plant_id == models.Plant.id
    ).filter(models.UserMicrocontroller.user_id == user_id)
    if filters.get("type"):
        q = q.filter(models.Microcontroller.type.ilike(f"%{filters['type']}%"))
    if filters.get("name"):
        q = q.filter(models.Plant.name.ilike(f"%{filters['name']}%"))
    if filters.get("location"):
        q = q.filter(models.Microcontroller.location.ilike(f"%{filters['location']}%"))
    return q.all()
