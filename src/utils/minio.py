"""
Phone Call Service.

Copyright (C) 2025  Andrew Kozmin <syn.kolbasyn.06@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
