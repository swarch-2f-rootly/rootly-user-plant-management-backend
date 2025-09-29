import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.domain.plant import Plant as PlantDomain
from src.adapters.repositories.models import Plant as PlantModel
from src.core.ports.plant_repository import PlantRepository

class PlantRepositoryImpl(PlantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_plant(self, plant: PlantDomain) -> PlantDomain:
        new_plant = PlantModel(**plant.model_dump())
        self.session.add(new_plant)
        await self.session.commit()
        await self.session.refresh(new_plant)
        return PlantDomain.model_validate(new_plant)

    async def get_plant_by_id(self, plant_id: uuid.UUID) -> Optional[PlantDomain]:
        result = await self.session.execute(select(PlantModel).where(PlantModel.id == plant_id))
        plant = result.scalar_one_or_none()
        return PlantDomain.model_validate(plant) if plant else None

    async def get_plants_by_user_id(self, user_id: uuid.UUID) -> List[PlantDomain]:
        result = await self.session.execute(select(PlantModel).where(PlantModel.user_id == user_id))
        plants = result.scalars().all()
        return [PlantDomain.model_validate(plant) for plant in plants]

    async def get_all_plants(self) -> List[PlantDomain]:
        result = await self.session.execute(select(PlantModel))
        plants = result.scalars().all()
        return [PlantDomain.model_validate(plant) for plant in plants]

    async def update_plant(self, plant: PlantDomain) -> PlantDomain:
        existing_plant = await self.session.get(PlantModel, plant.id)
        if existing_plant:
            for key, value in plant.model_dump().items():
                setattr(existing_plant, key, value)
            await self.session.commit()
            await self.session.refresh(existing_plant)
            return PlantDomain.model_validate(existing_plant)
        return None

    async def delete_plant(self, plant_id: uuid.UUID) -> None:
        plant = await self.session.get(PlantModel, plant_id)
        if plant:
            await self.session.delete(plant)
            await self.session.commit()
