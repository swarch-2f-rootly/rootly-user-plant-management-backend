from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth import get_current_user

# Dependency para obtener sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency para obtener usuario autenticado desde JWT
def get_current_active_user(current_user=Depends(get_current_user)):
    # Aquí podrías agregar validaciones extra (ej: usuario activo, no bloqueado)
    return current_user
