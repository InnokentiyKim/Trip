from abc import abstractmethod

from src.apps.hotel.file_object.domain.models import FileObject
from src.common.interfaces import GatewayProto


class FileObjectGatewayProto(GatewayProto):
    @abstractmethod
    async def delete_multiple_objects(self, keys: list[str]) -> None:
        """Delete multiple objects from the storage in batches."""
        ...

    @abstractmethod
    async def generate_download_pre_signed_url(self, key: str, file_name: str, content_type: str) -> str:
        """Generate a pre-signed URL for accessing an object."""
        ...

    @abstractmethod
    async def generate_upload_pre_signed_url(self, key: str) -> str:
        """Generate a pre-signed URL for uploading an object to the storage."""
        ...

    @abstractmethod
    async def get_object(self, key: str) -> FileObject | None:
        """Retrieve a file object from the storage by the key."""
        ...

    @abstractmethod
    async def check_availability(self) -> None:
        """Check the availability of the storage."""
        ...

    @abstractmethod
    async def copy_object(self, source_key: str, destination_key: str) -> None:
        """
        Copies an object from a source to a destination.

        Args:
            source_key: The key of the source object.
            destination_key: The key for the destination object.

        Raises:
            ClientError: If there is an error with the S3 client, such as the bucket not existing
            or the client not having permission to access it.
        """
        ...

    @abstractmethod
    async def list_objects_keys(self, prefix: str = "") -> list[str]:
        """
        Lists objects in storage, returning a complete list.

        This method uses a paginator to automatically handle fetching all objects
        matching a prefix. It collects all results into a list and returns it.

        Args:
            prefix: Prefix to filter objects by.

        Returns:
            list[str]: A list of all found file objects keys.

        Raises:
            ClientError: If there is an error with the S3 client, such as the bucket not existing
            or the client not having permission to access it.
        """
        ...

    @abstractmethod
    async def put_object(self, file_object: FileObject) -> None:
        """Put object to storage bucket."""
        ...
