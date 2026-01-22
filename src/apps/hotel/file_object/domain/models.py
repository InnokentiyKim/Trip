from dataclasses import dataclass
from io import BytesIO
from typing import Any

from aiobotocore.response import StreamingBody


@dataclass
class FileObject:
    """
    Represent a file-like object in the remote storage.

    Attributes:
        bucket_name (str): The name of the S3 bucket where the object is stored.
        object_name (str): The key or name of the object within the S3 bucket.
        body (IOBase): The content of the object.
    """

    bucket_name: str
    object_name: str
    size: int
    body: StreamingBody | BytesIO
    tagging: Any = ""
    content_type: str = ""

    def __hash__(self):
        """Hash object name."""
        return hash(self.object_name)

    @property
    def storage_key(self):
        """Get a storage key."""
        return self.object_name.split("/")[-1]

    @property
    def key_prefix(self):
        """Get a key prefix."""
        return self.object_name.split("/")[0]
