from minio import Minio
from fastapi import UploadFile
from src.core.ports.file_storage import FileStorage
from src.config.settings import settings
from io import BytesIO

class MinioStorage(FileStorage):
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._create_bucket_if_not_exists()

    def _create_bucket_if_not_exists(self):
        found = self.client.bucket_exists(self.bucket_name)
        if not found:
            self.client.make_bucket(self.bucket_name)

    async def upload_file(self, file: UploadFile, file_name: str) -> str:
        content = await file.read()
        self.client.put_object(
            self.bucket_name,
            file_name,
            data=BytesIO(content),
            length=len(content),
            content_type=file.content_type
        )
        return file_name

    async def download_file(self, file_name: str):
        response = self.client.get_object(self.bucket_name, file_name)
        return response

    async def delete_file(self, file_name: str) -> None:
        self.client.remove_object(self.bucket_name, file_name)
