import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_devices_isolation(client: AsyncClient):
    """
    Test that users only see devices associated with their own plants.
    This addresses the issue where all devices were visible to all users.
    """
    
    # Create two different users
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    # User 1 creates a plant and associates a device
    plant1_response = await client.post("/api/v1/plants/", json={
        "user_id": user1_id,
        "name": "User 1 Plant",
        "species": "User 1 Species"
    })
    assert plant1_response.status_code == 201
    plant1_id = plant1_response.json()["id"]
    
    # Create a device
    device1_response = await client.post("/api/v1/devices/", json={
        "name": "User 1 Device",
        "description": "Device for User 1",
        "category": "microcontroller"
    })
    assert device1_response.status_code == 201
    device1_id = device1_response.json()["id"]
    
    # Associate device with user 1's plant
    assign_response = await client.post(f"/api/v1/plants/{plant1_id}/devices/{device1_id}")
    assert assign_response.status_code == 201
    
    # User 2 creates a plant and associates a different device
    plant2_response = await client.post("/api/v1/plants/", json={
        "user_id": user2_id,
        "name": "User 2 Plant",
        "species": "User 2 Species"
    })
    assert plant2_response.status_code == 201
    plant2_id = plant2_response.json()["id"]
    
    # Create another device
    device2_response = await client.post("/api/v1/devices/", json={
        "name": "User 2 Device",
        "description": "Device for User 2",
        "category": "sensor"
    })
    assert device2_response.status_code == 201
    device2_id = device2_response.json()["id"]
    
    # Associate device with user 2's plant
    assign_response = await client.post(f"/api/v1/plants/{plant2_id}/devices/{device2_id}")
    assert assign_response.status_code == 201
    
    # Verify user 1 only sees their device
    user1_devices_response = await client.get(f"/api/v1/devices/users/{user1_id}")
    assert user1_devices_response.status_code == 200
    user1_devices = user1_devices_response.json()
    assert len(user1_devices) == 1
    assert user1_devices[0]["id"] == device1_id
    assert user1_devices[0]["name"] == "User 1 Device"
    
    # Verify user 2 only sees their device
    user2_devices_response = await client.get(f"/api/v1/devices/users/{user2_id}")
    assert user2_devices_response.status_code == 200
    user2_devices = user2_devices_response.json()
    assert len(user2_devices) == 1
    assert user2_devices[0]["id"] == device2_id
    assert user2_devices[0]["name"] == "User 2 Device"
    
    # Verify that the global devices endpoint still shows all devices (for admin purposes)
    all_devices_response = await client.get("/api/v1/devices/")
    assert all_devices_response.status_code == 200
    all_devices = all_devices_response.json()
    assert len(all_devices) >= 2  # Should have both devices

@pytest.mark.asyncio
async def test_user_with_no_plants_sees_no_devices(client: AsyncClient):
    """Test that a user with no plants sees no devices"""
    user_with_no_plants_id = str(uuid.uuid4())
    
    # User should see no devices
    devices_response = await client.get(f"/api/v1/devices/users/{user_with_no_plants_id}")
    assert devices_response.status_code == 200
    devices = devices_response.json()
    assert len(devices) == 0

@pytest.mark.asyncio
async def test_device_shared_between_users(client: AsyncClient):
    """
    Test that a device can be associated with plants from different users.
    This tests the flexibility of the many-to-many relationship.
    """
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    # Create plants for both users
    plant1_response = await client.post("/api/v1/plants/", json={
        "user_id": user1_id,
        "name": "User 1 Plant",
        "species": "Species 1"
    })
    plant1_id = plant1_response.json()["id"]
    
    plant2_response = await client.post("/api/v1/plants/", json={
        "user_id": user2_id,
        "name": "User 2 Plant",
        "species": "Species 2"
    })
    plant2_id = plant2_response.json()["id"]
    
    # Create a shared device
    shared_device_response = await client.post("/api/v1/devices/", json={
        "name": "Shared Device",
        "description": "Device shared between users",
        "category": "microcontroller"
    })
    shared_device_id = shared_device_response.json()["id"]
    
    # Associate device with both plants
    await client.post(f"/api/v1/plants/{plant1_id}/devices/{shared_device_id}")
    await client.post(f"/api/v1/plants/{plant2_id}/devices/{shared_device_id}")
    
    # Both users should see the shared device
    user1_devices = await client.get(f"/api/v1/devices/users/{user1_id}")
    user2_devices = await client.get(f"/api/v1/devices/users/{user2_id}")
    
    assert len(user1_devices.json()) == 1
    assert len(user2_devices.json()) == 1
    assert user1_devices.json()[0]["id"] == shared_device_id
    assert user2_devices.json()[0]["id"] == shared_device_id
