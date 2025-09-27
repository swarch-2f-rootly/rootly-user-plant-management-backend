
# Handler FastAPI para dispositivos usando arquitectura hexagonal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth import get_current_user
from app.core.services.device_service import DeviceService
from app.adapters.repositories.device_repository import SQLAlchemyDeviceRepository
from app.core.domain.schemas import EnableRequest, DeviceAssociationRequest, DeviceUpdateRequest
from app.adapters.repositories import models

router = APIRouter(prefix="/api/user/devices", tags=["devices"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_device_service(db: Session = Depends(get_db)):
    repo = SQLAlchemyDeviceRepository(db)
    return DeviceService(repo)

@router.get("")
def list_devices(name: str = None, type: str = None, location: str = None,
                 current_user=Depends(get_current_user), service: DeviceService = Depends(get_device_service)):
    filters = {"name": name, "type": type, "location": location}
    rows = service.list_devices(current_user["user_id"], filters)
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

@router.post("")
def associate_device(body: DeviceAssociationRequest, current_user=Depends(get_current_user), service: DeviceService = Depends(get_device_service)):
    assoc = service.associate_device(current_user["user_id"], body.microcontroller_id, plant_id=body.plant_id, role=body.role)
    if not assoc:
        raise HTTPException(status_code=400, detail="association_exists_or_invalid")
    return {"message": "associated"}

@router.patch("/{device_id}")
def edit_device(device_id: str, body: DeviceUpdateRequest, current_user=Depends(get_current_user), service: DeviceService = Depends(get_device_service)):
    if not service.user_has_permission(current_user["user_id"], device_id, min_role="editor", user_claims=current_user.get("roles")):
        raise HTTPException(status_code=403, detail="forbidden: requires editor/owner")
    device = service.update_device(device_id, location=body.location, plant_id=body.plant_id, type=body.type)
    if not device:
        raise HTTPException(status_code=404, detail="device_not_found")
    plant = None
    if device.plant_id:
        plant = service.repo.db.query(models.Plant).filter_by(id=device.plant_id).first()
    return {
        "id": str(device.id),
        "unique_id": device.unique_id,
        "type": device.type,
        "location": device.location,
        "enabled": device.enabled,
        "plant": {"id": str(plant.id), "name": plant.name} if plant else None,
        "role": service.repo.get_user_association(current_user["user_id"], device_id).role
    }

@router.patch("/{device_id}/enabled")
def set_enabled(device_id: str, body: EnableRequest, current_user=Depends(get_current_user), service: DeviceService = Depends(get_device_service)):
    if not service.user_has_permission(current_user["user_id"], device_id, min_role="editor", user_claims=current_user.get("roles")):
        raise HTTPException(status_code=403, detail="forbidden: requires editor/owner")
    device = service.set_enabled(device_id, body.enabled)
    if not device:
        raise HTTPException(status_code=404, detail="device_not_found")
    return {"id": str(device.id), "enabled": device.enabled}

@router.delete("/{device_id}")
def unassociate_device(device_id: str, current_user=Depends(get_current_user), service: DeviceService = Depends(get_device_service)):
    if not service.user_has_permission(current_user["user_id"], device_id, min_role="owner", user_claims=current_user.get("roles")):
        raise HTTPException(status_code=403, detail="forbidden: requires owner")
    ok = service.delete_device_association(current_user["user_id"], device_id)
    if not ok:
        raise HTTPException(status_code=404, detail="association_not_found")
    return {"message": "unassociated"}
