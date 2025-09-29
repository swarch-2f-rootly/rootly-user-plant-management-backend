import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from src.core.domain.plant import PhysicalDeviceCategory

class PlantBase(BaseModel):
    name: str
    species: str
    description: str | None = None

class PlantCreate(PlantBase):
    user_id: uuid.UUID

class PlantUpdate(PlantBase):
    pass

class PlantResponse(PlantBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    photo_filename: str | None = None
    created_at: datetime
    updated_at: datetime

class PhysicalDeviceBase(BaseModel):
    name: str
    description: str | None = None
    version: str | None = None
    category: PhysicalDeviceCategory

class PhysicalDeviceCreate(PhysicalDeviceBase):
    pass

class PhysicalDeviceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    version: str | None = None
    category: PhysicalDeviceCategory | None = None

class PhysicalDeviceResponse(PhysicalDeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
