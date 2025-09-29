# **Project Context: User Plant Management Service (Python)**

## **1. Project Overview & Justification**

This service is a specialized component of the agricultural monitoring system, designed to manage all data related to plants. Its primary purpose is to provide a centralized system for storing, retrieving, and managing plant information, including botanical details and associated images. The service is essential for tracking plant species, their characteristics, and visual records throughout their lifecycle.

The service will implement a robust API for CRUD operations on plant data, with a secure and decoupled mechanism for handling image uploads to an S3-compatible object store (MinIO). It will ensure that the frontend applications can interact with plant data and images without directly accessing the storage infrastructure, enhancing security and abstraction.

---

## **2. Core Technologies**

- **Python**: Primary programming language for the service's business logic.
- **FastAPI**: High-performance web framework for building the API, offering async support and automatic documentation.
- **PostgreSQL**: Relational database for storing structured plant data.
- **SQLAlchemy**: ORM for elegant and efficient database operations.
- **Alembic**: Database migration tool for managing schema evolution.
- **MinIO**: S3-compatible object storage for storing plant photos.
- **Pydantic**: Data validation and settings management.
- **Docker & Docker Compose**: For containerization and consistent deployment environments.

---

## **3. Architectural Principles**

- **Hexagonal Architecture (Ports and Adapters)**: The core domain logic for plant management is completely decoupled from external concerns like the database, API framework, or file storage. The `src/core` layer defines the interfaces (ports), and the `src/adapters` layer provides the concrete implementations.

- **Clean Architecture**: A layered approach where dependencies flow inward. The central `domain` entities are independent of application logic and infrastructure, making the system resilient to changes in external technologies.

- **Domain-Driven Design (DDD)**: The service is modeled around the `Plant` aggregate, encapsulating its properties and lifecycle.

- **Dependency Injection**: Dependencies are injected via FastAPI's `Depends` system, promoting modularity, testability, and decoupling from the framework.

- **Repository Pattern**: Data access is abstracted through repository interfaces, isolating the core logic from the specifics of the database implementation.

- **Clean Code**: Adherence to PEP 8, emphasis on readability, descriptive naming, and clear, concise functions.

---

## **4. API Endpoints**

The service will expose RESTful endpoints for managing plant information and photos.

### **Plant Management Endpoints:**

- **POST /api/v1/plants**
  - **Function**: Create a new plant entry.
  - **Request Body**: JSON object with plant details (e.g., `name`, `species`, `description`). The photo is handled separately.
  - **Response**: `201 Created` with the details of the newly created plant.

- **GET /api/v1/plants**
  - **Function**: Retrieve a list of all plants.
  - **Response**: `200 OK` with a list of plant objects.

- **GET /api/v1/plants/{plant_id}**
  - **Function**: Get detailed information for a specific plant.
  - **Response**: `200 OK` with the plant's complete details.

- **PUT /api/v1/plants/{plant_id}**
  - **Function**: Update a plant's information.
  - **Request Body**: JSON object with the fields to be updated.
  - **Response**: `200 OK` with the updated plant data.

- **DELETE /api/v1/plants/{plant_id}**
  - **Function**: Delete a plant entry.
  - **Response**: `204 No Content`.

### **Plant Photo Management Endpoints:**

- **POST /api/v1/plants/{plant_id}/photo**
  - **Function**: Upload a photo for a specific plant. The service will store it in MinIO and link the photo's identifier to the plant record in the database.
  - **Request**: `multipart/form-data` with the image file.
  - **Response**: `200 OK` with the URL to access the photo.

- **GET /api/v1/plants/{plant_id}/photo**
  - **Function**: Retrieve the photo for a specific plant. This endpoint will stream the image from MinIO, acting as a proxy so the frontend doesn't need direct bucket access.
  - **Response**: `200 OK` with the image file (`image/jpeg`, `image/png`, etc.).

- **DELETE /api/v1/plants/{plant_id}/photo**
  - **Function**: Delete a plant's photo.
  - **Response**: `204 No Content`.

### **User-Specific Plant Endpoints:**

- **GET /api/v1/users/{user_id}/plants**
  - **Function**: Retrieve all plants owned by a specific user.
  - **Response**: `200 OK` with a list of plant objects owned by the user.

### **Physical Devices Management Endpoints:**

- **POST /api/v1/devices**
  - **Function**: Create a new physical device (microcontroller or sensor).
  - **Request Body**: JSON object with device details (`name`, `description`, `version`, `category`).
  - **Response**: `201 Created` with the details of the newly created device.

- **GET /api/v1/devices**
  - **Function**: Retrieve a list of all physical devices.
  - **Response**: `200 OK` with a list of device objects.

- **GET /api/v1/devices/{device_id}**
  - **Function**: Get detailed information for a specific physical device.
  - **Response**: `200 OK` with the device's complete details.

- **PUT /api/v1/devices/{device_id}**
  - **Function**: Update a physical device's information.
  - **Request Body**: JSON object with the fields to be updated.
  - **Response**: `200 OK` with the updated device data.

- **DELETE /api/v1/devices/{device_id}**
  - **Function**: Delete a physical device entry.
  - **Response**: `204 No Content`.

### **Plant-Device Association Endpoints:**

- **POST /api/v1/plants/{plant_id}/devices/{device_id}**
  - **Function**: Associate a physical device with a plant.
  - **Response**: `201 Created` confirming the association.

- **DELETE /api/v1/plants/{plant_id}/devices/{device_id}**
  - **Function**: Remove the association between a plant and a physical device.
  - **Response**: `204 No Content`.

- **GET /api/v1/plants/{plant_id}/devices**
  - **Function**: Get all physical devices associated with a specific plant.
  - **Response**: `200 OK` with a list of devices associated with the plant.

---

## **5. Database Schema**

### **Core Entities:**

#### **Plants Entity:**
- **Purpose**: Stores the core information about each plant.
- **Key Fields**:
  - `id`: UUID primary key.
  - `name`: Common name of the plant.
  - `species`: Scientific name or species.
  - `description`: Textual description of the plant's characteristics.
  - `photo_filename`: String field containing the filename of the photo stored in MinIO. This is used to construct the access path.
  - `created_at`, `updated_at`: Audit timestamps.

### **Database Schema SQL:**

```sql
-- Physical devices table (microcontrollers and sensors)
CREATE TABLE physical_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    version VARCHAR(50),
    category VARCHAR(20) NOT NULL CHECK (category IN ('microcontroller', 'sensor')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plants table
CREATE TABLE plants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Owner of the plant (mandatory)
    name VARCHAR(100) NOT NULL,
    species VARCHAR(100),
    description TEXT,
    photo_filename VARCHAR(255), -- Name of the file stored in MinIO
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plant physical devices junction table (Many-to-Many)
CREATE TABLE plant_physical_devices (
    plant_id UUID REFERENCES plants(id) ON DELETE CASCADE,
    physical_device_id UUID REFERENCES physical_devices(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (plant_id, physical_device_id)
);

-- Indexes for performance
CREATE INDEX idx_physical_devices_name ON physical_devices(name);
CREATE INDEX idx_physical_devices_category ON physical_devices(category);
CREATE INDEX idx_plants_user_id ON plants(user_id);
CREATE INDEX idx_plants_name ON plants(name);
CREATE INDEX idx_plants_species ON plants(species);
CREATE INDEX idx_plant_physical_devices_plant ON plant_physical_devices(plant_id);
CREATE INDEX idx_plant_physical_devices_device ON plant_physical_devices(physical_device_id);
```

---

## **6. Project Structure & Naming Conventions**

The project will adopt the Hexagonal Architecture structure.

```
src/
├── core/                          # Business Logic Layer
│   ├── domain/                    # Domain Entities
│   │   ├── plant.py               # Plant aggregate
│   │   └── __init__.py
│   ├── ports/                     # Interfaces/Ports
│   │   ├── plant_repository.py    # Data access interface for plants
│   │   ├── file_storage.py        # File storage interface
│   │   └── __init__.py
│   └── services/                  # Application Services (Use Cases)
│       ├── plant_service.py       # Business logic for plant management
│       └── __init__.py
├── adapters/                      # Infrastructure Layer
│   ├── api/                       # API layer (FastAPI)
│   │   ├── routers/
│   │   │   └── plants.py          # Handlers for plant endpoints
│   │   ├── schemas.py             # Pydantic models for request/response
│   │   └── __init__.py
│   ├── repositories/              # Data Access Implementations
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── plant_repository_impl.py # PostgreSQL plant repository
│   │   └── __init__.py
│   └── storage/                   # File Storage Implementations
│       ├── minio_storage.py       # MinIO file storage implementation
│       └── __init__.py
├── config/                        # Configuration Management
│   ├── settings.py                # Application settings (Pydantic)
│   ├── database.py                # Database session management
│   └── __init__.py
└── main.py                        # Application Entry Point
```

---

## **7. File Upload & Storage Architecture**

### **MinIO Configuration:**
- **Bucket**: A dedicated bucket, e.g., `plant-photos`.
- **Access Policy**: Private by default. The service will use credentials to access it.
- **File Organization**: Files can be stored with a unique name, possibly a UUID, to avoid collisions. E.g., `{plant_id}/{uuid}.jpg`.

### **Upload Process:**
1. The client sends a `POST` request to `/api/v1/plants/{plant_id}/photo` with an image.
2. The API handler validates the file (type, size).
3. The `PlantService` uses the `FileStorage` port to save the file to MinIO, generating a unique filename.
4. The service updates the corresponding plant record in the database with the new `photo_filename`.

### **Retrieval Process:**
1. The client requests `GET /api/v1/plants/{plant_id}/photo`.
2. The API handler fetches the plant's metadata from the database to get the `photo_filename`.
3. The service streams the file from MinIO directly to the client as a response.

---

## **8. Testing Strategy**

- **Unit Tests**: Test the domain logic in `core/domain` and `core/services` in isolation. Mocks will be used for ports (repositories, storage).
- **Integration Tests**: Test the full request/response cycle of the API endpoints. These tests will interact with a real test database and a MinIO instance to ensure all parts of the system work together correctly.

---

## **9. Deployment & Infrastructure**

- **Docker**: The application will be containerized using a `Dockerfile`.
- **Docker Compose**: The `docker-compose.yml` in the `rootly-deployment` project will manage the service, its database, and the MinIO instance.
- **Database Migrations**: Alembic migrations will be configured to run automatically when the container starts up to ensure the database schema is always up-to-date.
