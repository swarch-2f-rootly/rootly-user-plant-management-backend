# Servicio de dominio para dispositivos
from typing import List, Optional
from uuid import UUID
from src.core.ports.repositories import DeviceRepositoryPort
from src.core.domain.entities import Microcontroller

class DeviceService:
    def __init__(self, repo: DeviceRepositoryPort):
        self.repo = repo

    def list_devices(self, user_id: UUID, filters: dict):
        return self.repo.get_devices_for_user(user_id, filters)

    def set_enabled(self, device_id: UUID, enabled: bool):
        return self.repo.set_enabled(device_id, enabled)

    def user_has_permission(self, user_id: UUID, device_id: UUID, min_role: str, user_claims=None):
        return self.repo.user_has_permission(user_id, device_id, min_role, user_claims)

    def associate_device(self, user_id, microcontroller_id, plant_id=None, role="viewer"):
        return self.repo.associate_device(user_id, microcontroller_id, plant_id, role)

    def delete_device_association(self, user_id, device_id):
        return self.repo.delete_device_association(user_id, device_id)

    def update_device(self, device_id, location=None, plant_id=None, type=None):
        return self.repo.update_device(device_id, location, plant_id, type)
