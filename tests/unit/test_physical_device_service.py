import pytest
import uuid
from unittest.mock import AsyncMock
from src.core.services.physical_device_service import PhysicalDeviceService
from src.core.domain.plant import PhysicalDevice

@pytest.fixture
def mock_device_repository():
    return AsyncMock()

@pytest.fixture
def device_service(mock_device_repository):
    return PhysicalDeviceService(mock_device_repository)

@pytest.mark.asyncio
async def test_create_device_service(device_service, mock_device_repository):
    mock_device_repository.create_device.return_value = PhysicalDevice(
        name="Test Device", description="A test device", category="microcontroller"
    )

    device = await device_service.create_device(name="Test Device", description="A test device", category="microcontroller")

    assert device.name == "Test Device"
    mock_device_repository.create_device.assert_called_once()

@pytest.mark.asyncio
async def test_assign_device_to_plant_service(device_service, mock_device_repository):
    plant_id = uuid.uuid4()
    device_id = uuid.uuid4()

    await device_service.assign_device_to_plant(plant_id, device_id)

    mock_device_repository.assign_device_to_plant.assert_called_once_with(plant_id, device_id)

@pytest.mark.asyncio
async def test_remove_device_from_plant_service(device_service, mock_device_repository):
    plant_id = uuid.uuid4()
    device_id = uuid.uuid4()

    await device_service.remove_device_from_plant(plant_id, device_id)

    mock_device_repository.remove_device_from_plant.assert_called_once_with(plant_id, device_id)
