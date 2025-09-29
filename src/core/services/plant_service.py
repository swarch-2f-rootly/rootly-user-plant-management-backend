import uuid
from typing import List, Optional
from src.core.domain.plant import Plant
from src.core.ports.plant_repository import PlantRepository
from src.core.ports.file_storage import FileStorage
from fastapi import UploadFile

class PlantService:
    def __init__(self, plant_repository: PlantRepository, file_storage: FileStorage):
        self.plant_repository = plant_repository
        self.file_storage = file_storage

    async def create_plant(self, user_id: uuid.UUID, name: str, species: str, description: Optional[str] = None) -> Plant:
        plant = Plant(user_id=user_id, name=name, species=species, description=description)
        return await self.plant_repository.create_plant(plant)

    async def get_plant_by_id(self, plant_id: uuid.UUID) -> Optional[Plant]:
        return await self.plant_repository.get_plant_by_id(plant_id)

    async def get_plants_by_user_id(self, user_id: uuid.UUID) -> List[Plant]:
        return await self.plant_repository.get_plants_by_user_id(user_id)

    async def get_all_plants(self) -> List[Plant]:
        return await self.plant_repository.get_all_plants()

    async def update_plant(self, plant_id: uuid.UUID, name: str, species: str, description: Optional[str] = None) -> Optional[Plant]:
        plant = await self.plant_repository.get_plant_by_id(plant_id)
        if plant:
            plant.name = name
            plant.species = species
            plant.description = description
            return await self.plant_repository.update_plant(plant)
        return None

    async def delete_plant(self, plant_id: uuid.UUID) -> None:
        plant = await self.plant_repository.get_plant_by_id(plant_id)
        if plant and plant.photo_filename:
            await self.file_storage.delete_file(plant.photo_filename)
        await self.plant_repository.delete_plant(plant_id)

    async def upload_plant_photo(self, plant_id: uuid.UUID, file: UploadFile) -> Optional[Plant]:
        plant = await self.plant_repository.get_plant_by_id(plant_id)
        if plant:
            if plant.photo_filename:
                await self.file_storage.delete_file(plant.photo_filename)
            
            file_extension = file.filename.split('.')[-1]
            photo_filename = f"{uuid.uuid4()}.{file_extension}"
            
            await self.file_storage.upload_file(file, photo_filename)
            plant.photo_filename = photo_filename
            return await self.plant_repository.update_plant(plant)
        return None

    async def get_plant_photo(self, plant_id: uuid.UUID):
        plant = await self.plant_repository.get_plant_by_id(plant_id)
        if plant and plant.photo_filename:
            return await self.file_storage.download_file(plant.photo_filename)
        return None

    async def delete_plant_photo(self, plant_id: uuid.UUID) -> Optional[Plant]:
        plant = await self.plant_repository.get_plant_by_id(plant_id)
        if plant and plant.photo_filename:
            await self.file_storage.delete_file(plant.photo_filename)
            plant.photo_filename = None
            return await self.plant_repository.update_plant(plant)
        return None
