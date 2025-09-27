
from fastapi import FastAPI
from app.adapters.handlers import device_handler

# Inicializamos app
app = FastAPI(
    title="Rootly User Plant Management Backend",
    description="Microservicio para gestionar usuarios, plantas y microcontroladores",
    version="0.1.0",
)

# Incluir routers
app.include_router(device_handler.router)

# Healthcheck básico
@app.get("/health")
def health():
    return {"status": "ok"}
