import uuid
from typing import List, Optional
from src.core.domain.plant import PhysicalDevice
from src.core.ports.plant_repository import PhysicalDeviceRepository

class PhysicalDeviceService:
    def __init__(self, device_repository: PhysicalDeviceRepository):
        self.device_repository = device_repository

    async def create_device(self, name: str, description: Optional[str] = None,
                          version: Optional[str] = None, category: str = "microcontroller") -> PhysicalDevice:
        device = PhysicalDevice(name=name, description=description, version=version, category=category)
        return await self.device_repository.create_device(device)

    async def get_device_by_id(self, device_id: uuid.UUID) -> Optional[PhysicalDevice]:
        return await self.device_repository.get_device_by_id(device_id)

    async def get_all_devices(self) -> List[PhysicalDevice]:
        return await self.device_repository.get_all_devices()

    async def update_device(self, device_id: uuid.UUID, name: str,
                          description: Optional[str] = None, version: Optional[str] = None,
                          category: Optional[str] = None) -> Optional[PhysicalDevice]:
        device = await self.device_repository.get_device_by_id(device_id)
        if device:
            device.name = name
            if description is not None:
                device.description = description
            if version is not None:
                device.version = version
            if category is not None:
                device.category = category
            return await self.device_repository.update_device(device)
        return None

    async def delete_device(self, device_id: uuid.UUID) -> None:
        return await self.device_repository.delete_device(device_id)

    async def get_devices_by_plant_id(self, plant_id: uuid.UUID) -> List[PhysicalDevice]:
        return await self.device_repository.get_devices_by_plant_id(plant_id)

    async def assign_device_to_plant(self, plant_id: uuid.UUID, device_id: uuid.UUID) -> None:
        return await self.device_repository.assign_device_to_plant(plant_id, device_id)

    async def remove_device_from_plant(self, plant_id: uuid.UUID, device_id: uuid.UUID) -> None:
        return await self.device_repository.remove_device_from_plant(plant_id, device_id)
