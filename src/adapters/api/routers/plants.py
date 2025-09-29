import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.services.plant_service import PlantService
from src.core.services.physical_device_service import PhysicalDeviceService
from src.adapters.api.schemas import PlantCreate, PlantUpdate, PlantResponse, PhysicalDeviceResponse
from src.config.database import get_session
from src.adapters.repositories.plant_repository_impl import PlantRepositoryImpl
from src.adapters.repositories.physical_device_repository_impl import PhysicalDeviceRepositoryImpl
from src.adapters.storage.minio_storage import MinioStorage

router = APIRouter(
    prefix="/api/v1/plants",
    tags=["plants"],
)

# Separate router for user-specific endpoints to avoid path conflicts
user_router = APIRouter(
    prefix="/api/v1/plants/users",
    tags=["plants"],
)

def get_plant_service(session: AsyncSession = Depends(get_session)) -> PlantService:
    plant_repository = PlantRepositoryImpl(session)
    file_storage = MinioStorage()
    return PlantService(plant_repository, file_storage)

def get_device_service(session: AsyncSession = Depends(get_session)) -> PhysicalDeviceService:
    device_repository = PhysicalDeviceRepositoryImpl(session)
    return PhysicalDeviceService(device_repository)

# User-specific plant endpoints in separate router
@user_router.get("/{user_id}", response_model=List[PlantResponse])
async def get_user_plants(user_id: uuid.UUID, service: PlantService = Depends(get_plant_service)):
    return await service.get_plants_by_user_id(user_id)

@router.post("/", response_model=PlantResponse, status_code=201)
async def create_plant(plant: PlantCreate, service: PlantService = Depends(get_plant_service)):
    return await service.create_plant(plant.user_id, plant.name, plant.species, plant.description)

@router.get("/", response_model=List[PlantResponse])
async def get_all_plants(service: PlantService = Depends(get_plant_service)):
    return await service.get_all_plants()

@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(plant_id: uuid.UUID, service: PlantService = Depends(get_plant_service)):
    plant = await service.get_plant_by_id(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant

@router.put("/{plant_id}", response_model=PlantResponse)
async def update_plant(plant_id: uuid.UUID, plant: PlantUpdate, service: PlantService = Depends(get_plant_service)):
    updated_plant = await service.update_plant(plant_id, plant.name, plant.species, plant.description)
    if not updated_plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return updated_plant

@router.delete("/{plant_id}", status_code=204)
async def delete_plant(plant_id: uuid.UUID, service: PlantService = Depends(get_plant_service)):
    await service.delete_plant(plant_id)

# Plant-device association endpoints
@router.post("/{plant_id}/devices/{device_id}", status_code=201)
async def assign_device_to_plant(plant_id: uuid.UUID, device_id: uuid.UUID,
                                plant_service: PlantService = Depends(get_plant_service),
                                device_service: PhysicalDeviceService = Depends(get_device_service)):
    # Verify plant exists
    plant = await plant_service.get_plant_by_id(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    # Verify device exists
    device = await device_service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    await device_service.assign_device_to_plant(plant_id, device_id)
    return {"message": "Device assigned to plant successfully"}

@router.delete("/{plant_id}/devices/{device_id}", status_code=204)
async def remove_device_from_plant(plant_id: uuid.UUID, device_id: uuid.UUID,
                                  device_service: PhysicalDeviceService = Depends(get_device_service)):
    await device_service.remove_device_from_plant(plant_id, device_id)

@router.get("/{plant_id}/devices", response_model=List[PhysicalDeviceResponse])
async def get_plant_devices(plant_id: uuid.UUID, plant_service: PlantService = Depends(get_plant_service),
                           device_service: PhysicalDeviceService = Depends(get_device_service)):
    # Verify plant exists
    plant = await plant_service.get_plant_by_id(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return await device_service.get_devices_by_plant_id(plant_id)

@router.post("/{plant_id}/photo", response_model=PlantResponse)
async def upload_photo(plant_id: uuid.UUID, file: UploadFile = File(...), service: PlantService = Depends(get_plant_service)):
    plant = await service.upload_plant_photo(plant_id, file)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant

@router.get("/{plant_id}/photo")
async def get_photo(plant_id: uuid.UUID, service: PlantService = Depends(get_plant_service)):
    photo_stream = await service.get_plant_photo(plant_id)
    if not photo_stream:
        raise HTTPException(status_code=404, detail="Photo not found")
    return StreamingResponse(photo_stream)

@router.delete("/{plant_id}/photo", response_model=PlantResponse)
async def delete_photo(plant_id: uuid.UUID, service: PlantService = Depends(get_plant_service)):
    plant = await service.delete_plant_photo(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant
