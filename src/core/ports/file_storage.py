from abc import ABC, abstractmethod
from fastapi import UploadFile

class FileStorage(ABC):
    @abstractmethod
    async def upload_file(self, file: UploadFile, file_name: str) -> str:
        pass

    @abstractmethod
    async def download_file(self, file_name: str):
        pass

    @abstractmethod
    async def delete_file(self, file_name: str) -> None:
        pass
