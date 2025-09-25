# app/routers/devices.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..auth import get_current_user
from .. import crud, models, schemas

router = APIRouter(prefix="/api/user/devices", tags=["devices"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
def list_devices(name: str = None, type: str = None, location: str = None,
                 current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    filters = {"name": name, "type": type, "location": location}
    rows = crud.list_devices_for_user(db, current_user["user_id"], filters)
    result = []
    for device, role, plant in rows:
        result.append({
            "id": str(device.id),
            "unique_id": device.unique_id,
            "type": device.type,
            "location": device.location,
            "enabled": device.enabled,
            "plant": {"id": str(plant.id), "name": plant.name} if plant else None,
            "role": role
        })
    return {"devices": result}

@router.patch("/{device_id}/enabled")
def set_enabled(device_id: str, body: schemas.EnableRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.user_has_permission(db, current_user["user_id"], device_id, min_role="editor", user_claims=current_user.get("roles")):
        raise HTTPException(status_code=403, detail="forbidden: requires editor/owner")
    device = db.query(models.Microcontroller).filter_by(id=device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="device_not_found")
    device.enabled = body.enabled
    db.add(device)
    db.commit()
    # publish event to broker here (see recomendaciones)
    return {"id": str(device.id), "enabled": device.enabled}
