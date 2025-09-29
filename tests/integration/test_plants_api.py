import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_plant(client: AsyncClient):
    user_id = str(uuid.uuid4())
    response = await client.post("/api/v1/plants/", json={
        "user_id": user_id,
        "name": "Test Plant",
        "species": "Test Species",
        "description": "A test plant"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Plant"
    assert data["user_id"] == user_id
    assert "id" in data

@pytest.mark.asyncio
async def test_get_all_plants(client: AsyncClient):
    user_id = str(uuid.uuid4())
    await client.post("/api/v1/plants/", json={"user_id": user_id, "name": "Test Plant 1", "species": "Test Species 1"})
    await client.post("/api/v1/plants/", json={"user_id": user_id, "name": "Test Plant 2", "species": "Test Species 2"})

    response = await client.get("/api/v1/plants/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_get_plants_by_user(client: AsyncClient):
    user_id = str(uuid.uuid4())
    await client.post("/api/v1/plants/", json={"user_id": user_id, "name": "User Plant 1", "species": "Species 1"})
    await client.post("/api/v1/plants/", json={"user_id": user_id, "name": "User Plant 2", "species": "Species 2"})

    response = await client.get(f"/api/v1/plants/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(plant["user_id"] == user_id for plant in data)

@pytest.mark.asyncio
async def test_get_plant(client: AsyncClient):
    user_id = str(uuid.uuid4())
    create_response = await client.post("/api/v1/plants/", json={"user_id": user_id, "name": "Another Test Plant", "species": "Another Species"})
    plant_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/plants/{plant_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Another Test Plant"

@pytest.mark.asyncio
async def test_update_plant(client: AsyncClient):
    user_id = str(uuid.uuid4())
    create_response = await client.post("/api/v1/plants/", json={"user_id": user_id, "name": "Updatable Plant", "species": "Updatable Species"})
    plant_id = create_response.json()["id"]

    response = await client.put(f"/api/v1/plants/{plant_id}", json={"name": "Updated Plant", "species": "Updated Species", "description": "Updated description"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Plant"
    assert data["description"] == "Updated description"

@pytest.mark.asyncio
async def test_delete_plant(client: AsyncClient):
    user_id = str(uuid.uuid4())
    create_response = await client.post("/api/v1/plants/", json={"user_id": user_id, "name": "Deletable Plant", "species": "Deletable Species"})
    plant_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/plants/{plant_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/plants/{plant_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_assign_device_to_plant(client: AsyncClient):
    user_id = str(uuid.uuid4())

    # Create a plant
    plant_response = await client.post("/api/v1/plants/", json={
        "user_id": user_id,
        "name": "Test Plant",
        "species": "Test Species"
    })
    plant_id = plant_response.json()["id"]

    # Create a device
    device_response = await client.post("/api/v1/devices/", json={
        "name": "Test Device",
        "description": "Test microcontroller",
        "category": "microcontroller"
    })
    device_id = device_response.json()["id"]

    # Assign device to plant
    assign_response = await client.post(f"/api/v1/plants/{plant_id}/devices/{device_id}")
    assert assign_response.status_code == 201

    # Check that device is associated with plant
    devices_response = await client.get(f"/api/v1/plants/{plant_id}/devices")
    assert devices_response.status_code == 200
    devices_data = devices_response.json()
    assert len(devices_data) == 1
    assert devices_data[0]["id"] == device_id

@pytest.mark.asyncio
async def test_remove_device_from_plant(client: AsyncClient):
    user_id = str(uuid.uuid4())

    # Create a plant
    plant_response = await client.post("/api/v1/plants/", json={
        "user_id": user_id,
        "name": "Test Plant",
        "species": "Test Species"
    })
    plant_id = plant_response.json()["id"]

    # Create a device
    device_response = await client.post("/api/v1/devices/", json={
        "name": "Test Device",
        "description": "Test microcontroller",
        "category": "microcontroller"
    })
    device_id = device_response.json()["id"]

    # Assign device to plant
    await client.post(f"/api/v1/plants/{plant_id}/devices/{device_id}")

    # Remove device from plant
    remove_response = await client.delete(f"/api/v1/plants/{plant_id}/devices/{device_id}")
    assert remove_response.status_code == 204

    # Check that device is no longer associated with plant
    devices_response = await client.get(f"/api/v1/plants/{plant_id}/devices")
    assert devices_response.status_code == 200
    devices_data = devices_response.json()
    assert len(devices_data) == 0
