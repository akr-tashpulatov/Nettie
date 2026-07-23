from .aws_s3 import StorageService, storage_service


def get_storage_service() -> StorageService:
    return storage_service
