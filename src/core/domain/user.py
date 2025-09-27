# Entidad de usuario para el dominio
from uuid import UUID

class User:
    def __init__(self, id: UUID, username: str, email: str):
        self.id = id
        self.username = username
        self.email = email
