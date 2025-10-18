import uuid
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class PhysicalDeviceCategory(str, Enum):
    MICROCONTROLLER = "microcontroller"
    SENSOR = "sensor"

class PhysicalDevice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID  # Owner of the device (mandatory)
    name: str
    description: str | None = None
    version: str | None = None
    category: PhysicalDeviceCategory
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Plant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID  # Owner of the plant (mandatory)
    name: str
    species: str
    description: str | None = None
    photo_filename: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
