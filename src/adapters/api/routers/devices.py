import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.services.physical_device_service import PhysicalDeviceService
from src.adapters.api.schemas import PhysicalDeviceCreate, PhysicalDeviceUpdate, PhysicalDeviceResponse
from src.config.database import get_session
from src.adapters.repositories.physical_device_repository_impl import PhysicalDeviceRepositoryImpl

router = APIRouter(
    prefix="/api/v1/devices",
    tags=["devices"],
)

def get_device_service(session: AsyncSession = Depends(get_session)) -> PhysicalDeviceService:
    device_repository = PhysicalDeviceRepositoryImpl(session)
    return PhysicalDeviceService(device_repository)

@router.post("/", response_model=PhysicalDeviceResponse, status_code=201)
async def create_device(device: PhysicalDeviceCreate, service: PhysicalDeviceService = Depends(get_device_service)):
    return await service.create_device(device.name, device.description, device.version, device.category)

@router.get("/", response_model=List[PhysicalDeviceResponse])
async def get_all_devices(service: PhysicalDeviceService = Depends(get_device_service)):
    return await service.get_all_devices()

@router.get("/{device_id}", response_model=PhysicalDeviceResponse)
async def get_device(device_id: uuid.UUID, service: PhysicalDeviceService = Depends(get_device_service)):
    device = await service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.put("/{device_id}", response_model=PhysicalDeviceResponse)
async def update_device(device_id: uuid.UUID, device: PhysicalDeviceUpdate, service: PhysicalDeviceService = Depends(get_device_service)):
    updated_device = await service.update_device(
        device_id=device_id,
        name=device.name,
        description=device.description,
        version=device.version,
        category=device.category
    )
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device

@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: uuid.UUID, service: PhysicalDeviceService = Depends(get_device_service)):
    await service.delete_device(device_id)
