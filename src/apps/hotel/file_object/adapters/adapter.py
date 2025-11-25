import asyncio

from src.apps.hotel.file_object.domain.models import FileObject
from src.apps.hotel.file_object.application.interfaces.gateway import (
    FileObjectGatewayProto,
)
from aiobotocore.client import AioBaseClient
from src.config import Configs
from typing import Self
from types import TracebackType
from botocore.exceptions import ClientError, EndpointConnectionError


class S3FileObjectAdapter(FileObjectGatewayProto):
    def __init__(self, client: AioBaseClient, config: Configs) -> None:
        self.client = client
        self.config = config
        self.bucket_name = config.s3.bucket_name
        self.sample_files_prefix = config.s3.sample_files_prefix

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit async context manager."""
        return None

    async def generate_download_pre_signed_url(
        self, key: str, file_name: str, content_type: str
    ) -> str:
        """
        Generate a pre-signed URL for uploading an object to S3.

        This method uses the client's generate_presigned_url function to create a URL
        that allows uploading an object using the PUT method. The URL is valid for a
        specified duration (6000 seconds) and sets the content type to "multipart/form-data".
        The internal S3 endpoint is replaced with the public endpoint (s3_endpoint_public)
        to allow users to upload to CDN or localhost URLs.

        Args:
            key (str): The key (path) where the file will be stored in the S3 bucket.
            file_name (str): The name of the file to be used in the Content-Disposition header.
            content_type (str): The MIME type of the file being uploaded.

        Returns:
            str: The generated pre-signed URL for PUT access to upload an object with public endpoint.
        """
        pre_signed_url = await self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{file_name}"',
                "ResponseContentType": content_type,
            },
            ExpiresIn=6000,
        )

        # Replace internal S3 endpoint with public endpoint for user-facing URLs
        pre_signed_url = pre_signed_url.replace(
            self.config.s3.s3_endpoint,
            self.config.s3.s3_endpoint_public,
        )

        return str(pre_signed_url)

    async def generate_upload_pre_signed_url(self, key: str) -> str:
        """
        Generate a pre-signed URL for uploading an object to S3.

        This method uses the client's generate_presigned_url function to create a URL
        that allows uploading an object using the PUT method. The URL is valid for a
        specified duration (6000 seconds) and sets the content type to "multipart/form-data".
        The internal S3 endpoint is replaced with the public endpoint (s3_endpoint_public)
        to allow users to upload to CDN or localhost URLs.

        Args:
            key (str): The key (path) where the file will be stored in the S3 bucket.

        Returns:
            str: The generated pre-signed URL for PUT access to upload an object with public endpoint.
        """
        pre_signed_url = await self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ContentType": "multipart/form-data",
            },
            ExpiresIn=6000,
        )

        # Replace internal S3 endpoint with public endpoint for user-facing URLs
        pre_signed_url = pre_signed_url.replace(
            self.config.s3.s3_endpoint,
            self.config.s3.s3_endpoint_public,
        )

        return str(pre_signed_url)

    async def get_object(self, key: str) -> FileObject | None:
        """
        Retrieve an object from the S3 bucket.

        This method attempts to fetch an object from the configured S3 bucket
        using the specified key. It retrieves only a portion of the object (up to the configured
        download_size) using the Range parameter. In case of a failure, it logs an error
        message and returns None. If the object is successfully retrieved, it returns a
        FileObject instance containing the object details.

        Args:
            key (str): The key of the object to retrieve from the S3 bucket.

        Returns:
            FileObject | None: A FileObject instance containing the retrieved object's details
            if successful, or None in case of an error.
        """
        try:
            response = await self.client.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            real_object_size = int(response.get("ContentLength"))
        except ClientError:
            return None

        return FileObject(
            bucket_name=self.bucket_name,
            object_name=key,
            body=response["Body"],
            size=real_object_size,
        )

    async def delete_multiple_objects(self, keys: list[str]) -> None: ...

    async def check_availability(self) -> None:
        try:
            await asyncio.wait_for(
                self.client.head_bucket(Bucket=self.bucket_name), timeout=10
            )
        except TimeoutError:
            raise EndpointConnectionError(
                endpoint_url=self.client.meta.endpoint_url
            ) from None
        except (ClientError, EndpointConnectionError) as exc:
            raise exc

    async def copy_object(self, source_key: str, destination_key: str) -> None:
        copy_source = {"Bucket": self.bucket_name, "Key": source_key}

        try:
            await self.client.copy_object(
                Bucket=self.bucket_name,
                CopySource=copy_source,
                Key=destination_key,
            )
        except ClientError as exc:
            raise exc

    async def list_objects_keys(self, prefix: str = "") -> list[str]: ...

    async def put_object(self, file_object: FileObject) -> None: ...
