from abc import ABC, abstractmethod
import uuid
from typing import List, Optional
from src.core.domain.plant import Plant, PhysicalDevice

class PlantRepository(ABC):
    @abstractmethod
    async def create_plant(self, plant: Plant) -> Plant:
        pass

    @abstractmethod
    async def get_plant_by_id(self, plant_id: uuid.UUID) -> Optional[Plant]:
        pass

    @abstractmethod
    async def get_plants_by_user_id(self, user_id: uuid.UUID) -> List[Plant]:
        pass

    @abstractmethod
    async def get_all_plants(self) -> List[Plant]:
        pass

    @abstractmethod
    async def update_plant(self, plant: Plant) -> Plant:
        pass

    @abstractmethod
    async def delete_plant(self, plant_id: uuid.UUID) -> None:
        pass

class PhysicalDeviceRepository(ABC):
    @abstractmethod
    async def create_device(self, device: PhysicalDevice) -> PhysicalDevice:
        pass

    @abstractmethod
    async def get_device_by_id(self, device_id: uuid.UUID) -> Optional[PhysicalDevice]:
        pass

    @abstractmethod
    async def get_all_devices(self) -> List[PhysicalDevice]:
        pass

    @abstractmethod
    async def update_device(self, device: PhysicalDevice) -> PhysicalDevice:
        pass

    @abstractmethod
    async def delete_device(self, device_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def get_devices_by_plant_id(self, plant_id: uuid.UUID) -> List[PhysicalDevice]:
        pass

    @abstractmethod
    async def assign_device_to_plant(self, plant_id: uuid.UUID, device_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def remove_device_from_plant(self, plant_id: uuid.UUID, device_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def get_devices_by_user_id(self, user_id: uuid.UUID) -> List[PhysicalDevice]:
        pass

    @abstractmethod
    async def get_device_by_id_and_user(self, device_id: uuid.UUID, user_id: uuid.UUID) -> Optional[PhysicalDevice]:
        pass