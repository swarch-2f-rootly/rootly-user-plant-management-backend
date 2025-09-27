# Modelos ORM para SQLAlchemy (infraestructura)
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.sql import func
from app.database import Base

class Plant(Base):
    __tablename__ = "plants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    location = Column(String(200))
    owner_user_id = Column(UUID(as_uuid=True))
    image_url = Column(TEXT)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Microcontroller(Base):
    __tablename__ = "microcontrollers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unique_id = Column(String(128), unique=True, nullable=False)
    type = Column(String(50), nullable=False)
    location = Column(String(200))
    enabled = Column(Boolean, default=True)
    plant_id = Column(UUID(as_uuid=True), ForeignKey("plants.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class UserMicrocontroller(Base):
    __tablename__ = "user_microcontrollers"
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    microcontroller_id = Column(UUID(as_uuid=True), ForeignKey("microcontrollers.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(20), default="viewer", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())