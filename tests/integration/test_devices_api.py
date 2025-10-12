import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_device(client: AsyncClient):
    user_id = str(uuid.uuid4())
    response = await client.post("/api/v1/devices/", json={
        "user_id": user_id,
        "name": "ESP32 Board",
        "description": "Microcontroller board for IoT applications",
        "version": "1.0",
        "category": "microcontroller"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ESP32 Board"
    assert data["category"] == "microcontroller"
    assert data["user_id"] == user_id
    assert "id" in data

@pytest.mark.asyncio
async def test_get_all_devices(client: AsyncClient):
    user_id = str(uuid.uuid4())
    await client.post("/api/v1/devices/", json={
        "user_id": user_id,
        "name": "Arduino Uno",
        "description": "Basic microcontroller board",
        "category": "microcontroller"
    })
    await client.post("/api/v1/devices/", json={
        "user_id": user_id,
        "name": "DHT22 Sensor",
        "description": "Temperature and humidity sensor",
        "category": "sensor"
    })

    response = await client.get("/api/v1/devices/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_get_device(client: AsyncClient):
    user_id = str(uuid.uuid4())
    create_response = await client.post("/api/v1/devices/", json={
        "user_id": user_id,
        "name": "Raspberry Pi",
        "description": "Single board computer",
        "category": "microcontroller"
    })
    device_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/devices/{device_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Raspberry Pi"

@pytest.mark.asyncio
async def test_update_device(client: AsyncClient):
    user_id = str(uuid.uuid4())
    create_response = await client.post("/api/v1/devices/", json={
        "user_id": user_id,
        "name": "Test Device",
        "description": "Device for testing",
        "category": "microcontroller"
    })
    device_id = create_response.json()["id"]

    response = await client.put(f"/api/v1/devices/{device_id}", json={
        "name": "Updated Device",
        "description": "Updated description",
        "version": "2.0",
        "category": "microcontroller"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Device"
    assert data["version"] == "2.0"

@pytest.mark.asyncio
async def test_delete_device(client: AsyncClient):
    user_id = str(uuid.uuid4())
    create_response = await client.post("/api/v1/devices/", json={
        "user_id": user_id,
        "name": "Device to Delete",
        "description": "This device will be deleted",
        "category": "sensor"
    })
    device_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/devices/{device_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/devices/{device_id}")
    assert get_response.status_code == 404

# New tests for user ownership functionality
@pytest.mark.asyncio
async def test_get_user_devices(client: AsyncClient):
    """Test that users only see their own devices"""
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    # Create devices for user1
    await client.post("/api/v1/devices/", json={
        "user_id": user1_id,
        "name": "User 1 Device 1",
        "category": "microcontroller"
    })
    await client.post("/api/v1/devices/", json={
        "user_id": user1_id,
        "name": "User 1 Device 2",
        "category": "sensor"
    })
    
    # Create device for user2
    await client.post("/api/v1/devices/", json={
        "user_id": user2_id,
        "name": "User 2 Device",
        "category": "microcontroller"
    })
    
    # User1 should only see their devices
    user1_devices_response = await client.get(f"/api/v1/devices/users/{user1_id}")
    assert user1_devices_response.status_code == 200
    user1_devices = user1_devices_response.json()
    assert len(user1_devices) == 2
    assert all(device["user_id"] == user1_id for device in user1_devices)
    
    # User2 should only see their device
    user2_devices_response = await client.get(f"/api/v1/devices/users/{user2_id}")
    assert user2_devices_response.status_code == 200
    user2_devices = user2_devices_response.json()
    assert len(user2_devices) == 1
    assert all(device["user_id"] == user2_id for device in user2_devices)

@pytest.mark.asyncio
async def test_user_cannot_access_other_user_device(client: AsyncClient):
    """Test that users cannot access devices owned by other users"""
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    # User1 creates a device
    create_response = await client.post("/api/v1/devices/", json={
        "user_id": user1_id,
        "name": "User 1 Device",
        "category": "microcontroller"
    })
    device_id = create_response.json()["id"]
    
    # User2 tries to access User1's device
    response = await client.get(f"/api/v1/devices/users/{user2_id}/devices/{device_id}")
    assert response.status_code == 404
    
    # User2 tries to update User1's device
    response = await client.put(f"/api/v1/devices/users/{user2_id}/devices/{device_id}", json={
        "name": "Hacked Device",
        "category": "microcontroller"
    })
    assert response.status_code == 404
    
    # User2 tries to delete User1's device
    response = await client.delete(f"/api/v1/devices/users/{user2_id}/devices/{device_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_user_can_manage_own_devices(client: AsyncClient):
    """Test that users can manage their own devices"""
    user_id = str(uuid.uuid4())
    
    # Create device
    create_response = await client.post("/api/v1/devices/", json={
        "user_id": user_id,
        "name": "My Device",
        "category": "microcontroller"
    })
    device_id = create_response.json()["id"]
    
    # User can access their own device
    response = await client.get(f"/api/v1/devices/users/{user_id}/devices/{device_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "My Device"
    
    # User can update their own device
    response = await client.put(f"/api/v1/devices/users/{user_id}/devices/{device_id}", json={
        "name": "Updated Device",
        "category": "microcontroller"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Device"
    
    # User can delete their own device
    response = await client.delete(f"/api/v1/devices/users/{user_id}/devices/{device_id}")
    assert response.status_code == 204
    
    # Device should be gone
    response = await client.get(f"/api/v1/devices/users/{user_id}/devices/{device_id}")
    assert response.status_code == 404
