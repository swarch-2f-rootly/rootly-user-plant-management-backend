# Servicio de dominio para plantas
from typing import List
from uuid import UUID
from src.core.ports.repositories import PlantRepositoryPort
from src.core.domain.entities import Plant

class PlantService:
    def __init__(self, repo: PlantRepositoryPort):
        self.repo = repo

    def list_plants(self, user_id: UUID) -> List[Plant]:
        return self.repo.get_plants(user_id)
