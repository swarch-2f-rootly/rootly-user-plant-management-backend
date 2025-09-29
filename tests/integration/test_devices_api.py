import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_device(client: AsyncClient):
    response = await client.post("/api/v1/devices/", json={
        "name": "ESP32 Board",
        "description": "Microcontroller board for IoT applications",
        "version": "1.0",
        "category": "microcontroller"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ESP32 Board"
    assert data["category"] == "microcontroller"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_all_devices(client: AsyncClient):
    await client.post("/api/v1/devices/", json={
        "name": "Arduino Uno",
        "description": "Basic microcontroller board",
        "category": "microcontroller"
    })
    await client.post("/api/v1/devices/", json={
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
    create_response = await client.post("/api/v1/devices/", json={
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
    create_response = await client.post("/api/v1/devices/", json={
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
    create_response = await client.post("/api/v1/devices/", json={
        "name": "Device to Delete",
        "description": "This device will be deleted",
        "category": "sensor"
    })
    device_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/devices/{device_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/devices/{device_id}")
    assert get_response.status_code == 404
