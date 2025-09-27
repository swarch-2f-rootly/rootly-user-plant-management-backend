# Puertos (interfaces) para repositorios
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.core.domain.entities import Device, Plant, Microcontroller, User, UserMicrocontroller

class DeviceRepositoryPort(ABC):
    @abstractmethod
    def get_devices_for_user(self, user_id: UUID, filters: dict) -> list:
        pass

    @abstractmethod
    def set_enabled(self, device_id: UUID, enabled: bool) -> Optional[Microcontroller]:
        pass

    @abstractmethod
    def get_user_association(self, user_id: UUID, device_id: UUID) -> Optional[UserMicrocontroller]:
        pass

    @abstractmethod
    def user_has_permission(self, user_id: UUID, device_id: UUID, min_role: str, user_claims=None) -> bool:
        pass

    @abstractmethod
    def associate_device(self, user_id: UUID, microcontroller_id: UUID, plant_id: UUID = None, role: str = "viewer") -> object:
        pass

    @abstractmethod
    def delete_device_association(self, user_id: UUID, device_id: UUID) -> bool:
        pass

    @abstractmethod
    def update_device(self, device_id: UUID, location: str = None, plant_id: UUID = None, type: str = None) -> object:
        pass

    @abstractmethod
    def get_devices(self, user_id: str) -> List[Device]:
        pass

    @abstractmethod
    def add_device(self, device: Device):
        pass

    @abstractmethod
    def update_device_entity(self, device: Device):
        pass

    @abstractmethod
    def delete_device(self, device_id: str):
        pass

class PlantRepositoryPort(ABC):
    @abstractmethod
    def get_plants(self, user_id: str) -> List[Plant]:
        pass

class UserRepositoryPort(ABC):
    @abstractmethod
    def get_user(self, user_id: str) -> User:
        pass
