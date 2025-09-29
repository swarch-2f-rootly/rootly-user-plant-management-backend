# app/models.py
import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PhysicalDevice(Base):
    __tablename__ = "physical_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(50))
    category = Column(String(20), nullable=False)  # 'microcontroller' or 'sensor'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Plant(Base):
    __tablename__ = "plants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Owner of the plant (mandatory)
    name = Column(String(100), nullable=False)
    species = Column(String(100))
    description = Column(Text)
    photo_filename = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PlantPhysicalDevice(Base):
    __tablename__ = "plant_physical_devices"

    plant_id = Column(UUID(as_uuid=True), ForeignKey("plants.id", ondelete="CASCADE"), primary_key=True)
    physical_device_id = Column(UUID(as_uuid=True), ForeignKey("physical_devices.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
