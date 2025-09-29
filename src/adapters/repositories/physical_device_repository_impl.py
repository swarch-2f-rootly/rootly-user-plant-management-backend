import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, insert
from src.core.domain.plant import PhysicalDevice as PhysicalDeviceDomain
from src.adapters.repositories.models import PhysicalDevice as PhysicalDeviceModel, PlantPhysicalDevice
from src.core.ports.plant_repository import PhysicalDeviceRepository

class PhysicalDeviceRepositoryImpl(PhysicalDeviceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_device(self, device: PhysicalDeviceDomain) -> PhysicalDeviceDomain:
        new_device = PhysicalDeviceModel(**device.model_dump())
        self.session.add(new_device)
        await self.session.commit()
        await self.session.refresh(new_device)
        return PhysicalDeviceDomain.model_validate(new_device)

    async def get_device_by_id(self, device_id: uuid.UUID) -> Optional[PhysicalDeviceDomain]:
        result = await self.session.execute(select(PhysicalDeviceModel).where(PhysicalDeviceModel.id == device_id))
        device = result.scalar_one_or_none()
        return PhysicalDeviceDomain.model_validate(device) if device else None

    async def get_all_devices(self) -> List[PhysicalDeviceDomain]:
        result = await self.session.execute(select(PhysicalDeviceModel))
        devices = result.scalars().all()
        return [PhysicalDeviceDomain.model_validate(device) for device in devices]

    async def update_device(self, device: PhysicalDeviceDomain) -> PhysicalDeviceDomain:
        existing_device = await self.session.get(PhysicalDeviceModel, device.id)
        if existing_device:
            for key, value in device.model_dump().items():
                setattr(existing_device, key, value)
            await self.session.commit()
            await self.session.refresh(existing_device)
            return PhysicalDeviceDomain.model_validate(existing_device)
        return None

    async def delete_device(self, device_id: uuid.UUID) -> None:
        device = await self.session.get(PhysicalDeviceModel, device_id)
        if device:
            await self.session.delete(device)
            await self.session.commit()

    async def get_devices_by_plant_id(self, plant_id: uuid.UUID) -> List[PhysicalDeviceDomain]:
        query = select(PhysicalDeviceModel).join(
            PlantPhysicalDevice,
            PhysicalDeviceModel.id == PlantPhysicalDevice.physical_device_id
        ).where(PlantPhysicalDevice.plant_id == plant_id)

        result = await self.session.execute(query)
        devices = result.scalars().all()
        return [PhysicalDeviceDomain.model_validate(device) for device in devices]

    async def assign_device_to_plant(self, plant_id: uuid.UUID, device_id: uuid.UUID) -> None:
        await self.session.execute(
            insert(PlantPhysicalDevice).values(
                plant_id=plant_id,
                physical_device_id=device_id
            )
        )
        await self.session.commit()

    async def remove_device_from_plant(self, plant_id: uuid.UUID, device_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(PlantPhysicalDevice).where(
                PlantPhysicalDevice.plant_id == plant_id,
                PlantPhysicalDevice.physical_device_id == device_id
            )
        )
        await self.session.commit()
