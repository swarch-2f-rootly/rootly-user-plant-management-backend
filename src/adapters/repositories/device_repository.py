# Adaptador de repositorio SQLAlchemy
from src.core.ports.repositories import DeviceRepositoryPort
from src.adapters.repositories import models
from src.core.domain.entities import Microcontroller, UserMicrocontroller, Plant
from uuid import UUID

ROLE_LEVEL = {"viewer": 0, "editor": 1, "owner": 2}

class SQLAlchemyDeviceRepository(DeviceRepositoryPort):
    def __init__(self, db_session):
        self.db = db_session

    def get_devices_for_user(self, user_id: UUID, filters: dict):
        q = self.db.query(models.Microcontroller, models.UserMicrocontroller.role, models.Plant).join(
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

    def set_enabled(self, device_id: UUID, enabled: bool):
        device = self.db.query(models.Microcontroller).filter_by(id=device_id).first()
        if not device:
            return None
        device.enabled = enabled
        self.db.add(device)
        self.db.commit()
        return device

    def get_user_association(self, user_id: UUID, device_id: UUID):
        return self.db.query(models.UserMicrocontroller).filter_by(user_id=user_id, microcontroller_id=device_id).first()

    def user_has_permission(self, user_id: UUID, device_id: UUID, min_role="viewer", user_claims=None):
        if user_claims and "admin" in user_claims:
            return True
        assoc = self.get_user_association(user_id, device_id)
        if not assoc:
            return False
        return ROLE_LEVEL.get(assoc.role, 0) >= ROLE_LEVEL.get(min_role, 0)

    def associate_device(self, user_id: UUID, microcontroller_id: UUID, plant_id: UUID = None, role: str = "viewer"):
        # Verifica si ya existe la asociación
        assoc = self.db.query(models.UserMicrocontroller).filter_by(user_id=user_id, microcontroller_id=microcontroller_id).first()
        if assoc:
            return None  # Ya existe
        # Crea la asociación
        assoc = models.UserMicrocontroller(user_id=user_id, microcontroller_id=microcontroller_id, role=role)
        self.db.add(assoc)
        # Si se provee plant_id, actualiza el device
        device = self.db.query(models.Microcontroller).filter_by(id=microcontroller_id).first()
        if device and plant_id:
            device.plant_id = plant_id
            self.db.add(device)
        self.db.commit()
        return assoc

    def delete_device_association(self, user_id: UUID, device_id: UUID) -> bool:
        assoc = self.db.query(models.UserMicrocontroller).filter_by(user_id=user_id, microcontroller_id=device_id).first()
        if not assoc:
            return False
        self.db.delete(assoc)
        self.db.commit()
        return True

    def update_device(self, device_id: UUID, location: str = None, plant_id: UUID = None, type: str = None):
        device = self.db.query(models.Microcontroller).filter_by(id=device_id).first()
        if not device:
            return None
        if location is not None:
            device.location = location
        if plant_id is not None:
            device.plant_id = plant_id
        if type is not None:
            device.type = type
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device
