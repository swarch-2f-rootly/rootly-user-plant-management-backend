from app import models

def seed_device_and_assoc(db_session, user_id="user-1"):
    device = models.Microcontroller(id="dev-1", unique_id="UID123", type="ESP32")
    assoc = models.UserMicrocontroller(user_id=user_id, microcontroller_id="dev-1", role="owner")
    db_session.add_all([device, assoc])
    db_session.commit()
    return device

# --- Helpers ---
def seed_plant_and_device(db_session, user_id="user-1", device_id="dev-3", plant_name="Tomates"):
    plant = models.Plant(id="plant-1", name=plant_name, location="invernadero 1", owner_user_id=user_id)
    device = models.Microcontroller(id=device_id, unique_id=f"UID-{device_id}", type="ESP32", location="invernadero 1", plant_id="plant-1")
    assoc = models.UserMicrocontroller(user_id=user_id, microcontroller_id=device_id, role="owner")
    db_session.add_all([plant, device, assoc])
    db_session.commit()
    return plant, device

def test_list_devices(client, db_session, token_user_owner):
    seed_device_and_assoc(db_session)
    res = client.get("/api/user/devices", headers=token_user_owner)
    assert res.status_code == 200
    data = res.json()
    assert "devices" in data
    assert data["devices"][0]["unique_id"] == "UID123"

def test_enable_device_success(client, db_session, token_user_owner):
    seed_device_and_assoc(db_session)
    res = client.patch("/api/user/devices/dev-1/enabled",
                       json={"enabled": False},
                       headers=token_user_owner)
    assert res.status_code == 200
    data = res.json()
    assert data["enabled"] is False

def test_enable_device_forbidden(client, db_session, token_user_owner):
    # Creamos un device asociado a otro user
    device = models.Microcontroller(id="dev-2", unique_id="UID456", type="ESP8266")
    assoc = models.UserMicrocontroller(user_id="user-other", microcontroller_id="dev-2", role="owner")
    db_session.add_all([device, assoc])
    db_session.commit()

    res = client.patch("/api/user/devices/dev-2/enabled",
                       json={"enabled": False},
                       headers=token_user_owner)
    assert res.status_code == 403
    assert res.json()["detail"].startswith("forbidden")

# --- FR-D2: editar asociación ---
def test_edit_device_location_and_plant(client, db_session, token_user_owner):
    # Seed inicial
    plant, device = seed_plant_and_device(db_session, user_id="user-1", device_id="dev-4", plant_name="Lechugas")
    new_plant = models.Plant(id="plant-2", name="Tomates", location="invernadero 2", owner_user_id="user-1")
    db_session.add(new_plant)
    db_session.commit()

    body = {"location": "invernadero central", "plant_id": "plant-2"}
    res = client.patch(f"/api/user/devices/{device.id}", json=body, headers=token_user_owner)

    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "invernadero central"
    assert data["plant"]["id"] == "plant-2"

def test_edit_device_forbidden_if_not_owner_or_editor(client, db_session, token_user_owner):
    # Device con otro dueño
    plant, device = seed_plant_and_device(db_session, user_id="user-other", device_id="dev-5")
    res = client.patch(f"/api/user/devices/{device.id}",
                       json={"location": "otro sitio"},
                       headers=token_user_owner)
    assert res.status_code == 403
    assert res.json()["detail"].startswith("forbidden")

# --- FR-D2: desasociar microcontrolador ---
def test_unassociate_device(client, db_session, token_user_owner):
    _, device = seed_plant_and_device(db_session, user_id="user-1", device_id="dev-6")
    res = client.delete(f"/api/user/devices/{device.id}", headers=token_user_owner)
    assert res.status_code == 200
    assert res.json()["message"] == "unassociated"

    # Ya no debe estar la asociación en DB
    assoc = db_session.query(models.UserMicrocontroller).filter_by(user_id="user-1", microcontroller_id="dev-6").first()
    assert assoc is None

def test_unassociate_forbidden_if_not_owner(client, db_session, token_user_owner):
    _, device = seed_plant_and_device(db_session, user_id="user-other", device_id="dev-7")
    res = client.delete(f"/api/user/devices/{device.id}", headers=token_user_owner)
    assert res.status_code == 403

# --- FR-D3: filtros de listado ---
def test_list_devices_filter_by_name(client, db_session, token_user_owner):
    # Creamos dos plantas con devices
    seed_plant_and_device(db_session, user_id="user-1", device_id="dev-8", plant_name="Tomates Cherry")
    seed_plant_and_device(db_session, user_id="user-1", device_id="dev-9", plant_name="Lechugas Hidro")

    res = client.get("/api/user/devices?name=Tomates", headers=token_user_owner)
    assert res.status_code == 200
    data = res.json()["devices"]
    assert len(data) == 1
    assert "Tomates" in data[0]["plant"]["name"]

def test_list_devices_filter_by_type(client, db_session, token_user_owner):
    # Un device ESP32 y otro ESP8266
    seed_plant_and_device(db_session, user_id="user-1", device_id="dev-10")
    device2 = models.Microcontroller(id="dev-11", unique_id="UID-ESP8266", type="ESP8266", location="invernadero B")
    assoc = models.UserMicrocontroller(user_id="user-1", microcontroller_id="dev-11", role="owner")
    db_session.add_all([device2, assoc])
    db_session.commit()

    res = client.get("/api/user/devices?type=ESP8266", headers=token_user_owner)
    assert res.status_code == 200
    data = res.json()["devices"]
    assert len(data) == 1
    assert data[0]["type"] == "ESP8266"

def test_list_devices_filter_by_location(client, db_session, token_user_owner):
    seed_plant_and_device(db_session, user_id="user-1", device_id="dev-12")
    device2 = models.Microcontroller(id="dev-13", unique_id="UID-OTHER", type="ESP32", location="zona norte")
    assoc = models.UserMicrocontroller(user_id="user-1", microcontroller_id="dev-13", role="owner")
    db_session.add_all([device2, assoc])
    db_session.commit()

    res = client.get("/api/user/devices?location=norte", headers=token_user_owner)
    assert res.status_code == 200
    data = res.json()["devices"]
    assert len(data) == 1
    assert "norte" in data[0]["location"]
