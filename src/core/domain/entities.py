# Entidades de dominio (sin dependencias de SQLAlchemy)
from uuid import UUID
from typing import Optional

class Plant:
    def __init__(self, id: UUID, name: str, location: Optional[str] = None, owner_user_id: Optional[UUID] = None, image_url: Optional[str] = None):
        self.id = id
        self.name = name
        self.location = location
        self.owner_user_id = owner_user_id
        self.image_url = image_url

class Microcontroller:
    def __init__(self, id: UUID, unique_id: str, type: str, location: Optional[str] = None, enabled: bool = True, plant_id: Optional[UUID] = None):
        self.id = id
        self.unique_id = unique_id
        self.type = type
        self.location = location
        self.enabled = enabled
        self.plant_id = plant_id

class UserMicrocontroller:
    def __init__(self, user_id: UUID, microcontroller_id: UUID, role: str = "viewer"):
        self.user_id = user_id
        self.microcontroller_id = microcontroller_id
        self.role = role
