"""Seed data for plants, microcontrollers, and associations

Revision ID: seed123456
Revises: <id_de_init_schema>
Create Date: 2025-09-24

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid

# IDs de migración
revision = "seed123456"
down_revision = "<id_de_init_schema>"   # reemplaza con el hash de tu migración inicial
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()

    # Users simulados (referencias, aunque users reales están en rootly-auth)
    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())

    # Plants
    plant1 = str(uuid.uuid4())
    plant2 = str(uuid.uuid4())

    conn.execute(sa.text("""
        INSERT INTO plants (id, name, location, owner_user_id, created_at)
        VALUES (:id, :name, :location, :owner_user_id, :created_at)
    """), [
        {"id": plant1, "name": "Tomates Cherry", "location": "invernadero A", "owner_user_id": user1, "created_at": datetime.utcnow()},
        {"id": plant2, "name": "Lechugas Hidro", "location": "invernadero B", "owner_user_id": user2, "created_at": datetime.utcnow()},
    ])

    # Devices
    dev1 = str(uuid.uuid4())
    dev2 = str(uuid.uuid4())
    dev3 = str(uuid.uuid4())

    conn.execute(sa.text("""
        INSERT INTO microcontrollers (id, unique_id, type, location, enabled, plant_id, created_at)
        VALUES (:id, :unique_id, :type, :location, :enabled, :plant_id, :created_at)
    """), [
        {"id": dev1, "unique_id": "ESP32-ABC", "type": "ESP32", "location": "invernadero A", "enabled": True, "plant_id": plant1, "created_at": datetime.utcnow()},
        {"id": dev2, "unique_id": "ESP8266-XYZ", "type": "ESP8266", "location": "invernadero B", "enabled": True, "plant_id": plant2, "created_at": datetime.utcnow()},
        {"id": dev3, "unique_id": "ESP32-123", "type": "ESP32", "location": "zona norte", "enabled": False, "plant_id": plant1, "created_at": datetime.utcnow()},
    ])

    # Associations
    conn.execute(sa.text("""
        INSERT INTO user_microcontrollers (user_id, microcontroller_id, role, created_at)
        VALUES (:user_id, :microcontroller_id, :role, :created_at)
    """), [
        {"user_id": user1, "microcontroller_id": dev1, "role": "owner", "created_at": datetime.utcnow()},
        {"user_id": user1, "microcontroller_id": dev2, "role": "viewer", "created_at": datetime.utcnow()},
        {"user_id": user2, "microcontroller_id": dev3, "role": "owner", "created_at": datetime.utcnow()},
    ])

def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM user_microcontrollers"))
    conn.execute(sa.text("DELETE FROM microcontrollers"))
    conn.execute(sa.text("DELETE FROM plants"))
