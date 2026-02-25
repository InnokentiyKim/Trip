from dataclasses import dataclass
from io import BytesIO
from typing import Any
from uuid import UUID

from aiobotocore.response import StreamingBody

from src.apps.hotel.file_object.domain.models import FileObject


@dataclass(slots=True, frozen=True)
class UploadInfo:
    url: str
    storage_key: UUID


@dataclass(slots=True, frozen=True)
class FileObjectInfo:
    bucket_name: str
    storage_key: str
    key_prefix: str
    size: int
    object_name: str
    body: StreamingBody | BytesIO
    tagging: Any = ""
    content_type: str = ""

    @classmethod
    def from_model(cls, file_object: FileObject) -> "FileObjectInfo":
        """Create file object info from the file object model."""
        return cls(
            bucket_name=file_object.bucket_name,
            storage_key=file_object.storage_key,
            key_prefix=file_object.key_prefix,
            size=file_object.size,
            body=file_object.body,
            tagging=file_object.tagging,
            content_type=file_object.content_type,
            object_name=file_object.object_name,
        )
