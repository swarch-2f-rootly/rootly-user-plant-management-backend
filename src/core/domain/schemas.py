# Schemas de dominio (Pydantic)
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

# --- Requests ---
class DeviceAssociationRequest(BaseModel):
    microcontroller_id: UUID
    plant_id: Optional[UUID] = None
    role: str = Field(default="viewer", pattern="^(owner|editor|viewer)$")

class DeviceUpdateRequest(BaseModel):
    location: Optional[str] = None
    plant_id: Optional[UUID] = None
    type: Optional[str] = None

class EnableRequest(BaseModel):
    enabled: bool

# --- Responses ---
class PlantOut(BaseModel):
    id: UUID
    name: str
    class Config:
        orm_mode = True

class DeviceOut(BaseModel):
    id: UUID
    unique_id: str
    type: str
    location: Optional[str]
    enabled: bool
    role: str
    plant: Optional[PlantOut]
    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    message: str
