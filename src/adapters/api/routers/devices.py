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
    return await service.create_device(device.user_id, device.name, device.description, device.version, device.category)

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
    # For now, this endpoint doesn't require user_id (admin endpoint)
    # In production, you'd want to get user_id from JWT token
    updated_device = await service.get_device_by_id(device_id)
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device

@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: uuid.UUID, service: PhysicalDeviceService = Depends(get_device_service)):
    # For now, this endpoint doesn't require user_id (admin endpoint)
    # In production, you'd want to get user_id from JWT token
    await service.delete_device(device_id)

# User-specific endpoints with ownership validation
@router.put("/users/{user_id}/devices/{device_id}", response_model=PhysicalDeviceResponse)
async def update_user_device(user_id: uuid.UUID, device_id: uuid.UUID, device: PhysicalDeviceUpdate, service: PhysicalDeviceService = Depends(get_device_service)):
    updated_device = await service.update_device(
        user_id=user_id,
        device_id=device_id,
        name=device.name or "",  # Provide default values
        description=device.description,
        version=device.version,
        category=device.category
    )
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found or not owned by user")
    return updated_device

@router.delete("/users/{user_id}/devices/{device_id}", status_code=204)
async def delete_user_device(user_id: uuid.UUID, device_id: uuid.UUID, service: PhysicalDeviceService = Depends(get_device_service)):
    result = await service.delete_device(user_id, device_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Device not found or not owned by user")

@router.get("/users/{user_id}/devices/{device_id}", response_model=PhysicalDeviceResponse)
async def get_user_device(user_id: uuid.UUID, device_id: uuid.UUID, service: PhysicalDeviceService = Depends(get_device_service)):
    device = await service.get_device_by_id_and_user(device_id, user_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or not owned by user")
    return device

@router.get("/users/{user_id}", response_model=List[PhysicalDeviceResponse])
async def get_user_devices(user_id: uuid.UUID, service: PhysicalDeviceService = Depends(get_device_service)):
    """Get all devices owned by a specific user"""
    return await service.get_devices_by_user_id(user_id)