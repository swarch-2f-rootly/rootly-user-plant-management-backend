import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock
from src.core.services.plant_service import PlantService
from src.core.domain.plant import Plant

@pytest.fixture
def mock_plant_repository():
    return AsyncMock()

@pytest.fixture
def mock_file_storage():
    return AsyncMock()

@pytest.fixture
def plant_service(mock_plant_repository, mock_file_storage):
    return PlantService(mock_plant_repository, mock_file_storage)

@pytest.mark.asyncio
async def test_create_plant_service(plant_service, mock_plant_repository):
    user_id = uuid.uuid4()
    mock_plant_repository.create_plant.return_value = Plant(user_id=user_id, name="Test Plant", species="Test Species")

    plant = await plant_service.create_plant(user_id=user_id, name="Test Plant", species="Test Species")

    assert plant.name == "Test Plant"
    assert plant.user_id == user_id
    mock_plant_repository.create_plant.assert_called_once()

@pytest.mark.asyncio
async def test_get_plants_by_user_id_service(plant_service, mock_plant_repository):
    user_id = uuid.uuid4()
    plants = [
        Plant(user_id=user_id, name="Plant 1", species="Species 1"),
        Plant(user_id=user_id, name="Plant 2", species="Species 2")
    ]
    mock_plant_repository.get_plants_by_user_id.return_value = plants

    result = await plant_service.get_plants_by_user_id(user_id)

    assert len(result) == 2
    assert all(plant.user_id == user_id for plant in result)
    mock_plant_repository.get_plants_by_user_id.assert_called_once_with(user_id)

@pytest.mark.asyncio
async def test_delete_plant_with_photo_service(plant_service, mock_plant_repository, mock_file_storage):
    user_id = uuid.uuid4()
    plant_id = uuid.uuid4()
    plant_with_photo = Plant(id=plant_id, user_id=user_id, name="Test Plant", species="Test Species", photo_filename="test.jpg")
    mock_plant_repository.get_plant_by_id.return_value = plant_with_photo

    await plant_service.delete_plant(plant_id)

    mock_plant_repository.get_plant_by_id.assert_called_with(plant_id)
    mock_file_storage.delete_file.assert_called_with("test.jpg")
    mock_plant_repository.delete_plant.assert_called_with(plant_id)
