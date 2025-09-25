from minio import Minio

from config import Settings


def download_file_from_minio(object_name: str, file_path: str) -> None:
    minio_client = Minio(
        Settings().minio_endpoint,
        access_key=Settings().minio_access_key,
        secret_key=Settings().minio_secret_key,
        secure=True,
        cert_check=False,
    )
    minio_client.fget_object(
        bucket_name=Settings().minio_bucket_name,
        object_name=object_name,
        file_path=file_path,
    )
