import asyncio
from collections.abc import Generator
from itertools import islice
from types import TracebackType
from typing import Self

from aiobotocore.client import AioBaseClient
from aiobotocore.response import StreamingBody
from botocore.exceptions import ClientError, EndpointConnectionError

from src.apps.hotel.file_object.application.interfaces.gateway import (
    FileObjectGatewayProto,
)
from src.apps.hotel.file_object.domain.models import FileObject
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class S3FileObjectAdapter(FileObjectGatewayProto):
    def __init__(self, client: AioBaseClient, logger: CustomLoggerProto, config: Configs) -> None:
        self.client = client
        self.logger = logger
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

    async def generate_download_pre_signed_url(self, key: str, file_name: str, content_type: str) -> str:
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

    async def generate_upload_pre_signed_url(self, storage_key: str) -> str:
        """
        Generate a pre-signed URL for uploading an object to S3.

        This method uses the client's generate_presigned_url function to create a URL
        that allows uploading an object using the PUT method. The URL is valid for a
        specified duration (6000 seconds) and sets the content type to "multipart/form-data".
        The internal S3 endpoint is replaced with the public endpoint (s3_endpoint_public)
        to allow users to upload to CDN or localhost URLs.

        Args:
            storage_key (str): The key (path) where the file will be stored in the S3 bucket.

        Returns:
            str: The generated pre-signed URL for PUT access to upload an object with public endpoint.
        """
        pre_signed_url = await self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": storage_key,
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

    async def delete_multiple_objects(self, keys: list[str]) -> None:
        """
        Delete multiple objects from the S3 bucket in batches.

        This method deletes objects from the S3 bucket in chunks (batches) of up to 1000
        keys at a time, which is the maximum allowed by the S3 API. For each chunk, it
        constructs a list of objects to delete and sends a delete_objects request to S3.
        The method logs information about the deletion process, including the number of
        successfully deleted objects and any errors that occurred.

        Args:
            keys (list[str]): A list of object keys (filenames) to be deleted from the S3 bucket.

        Returns:
            None
        """
        # TODO: Add retry logic for handling errors returned from S3.

        def chunked(iterable: list[str], size: int = 1000) -> Generator[list[str]]:
            """
            Yield successive chunks of the specified size from the iterable.

            This helper function divides a list into smaller chunks of a specified size.
            It's used to break down large lists of keys into manageable batches for S3 operations.

            Args:
                iterable (list[str]): A list of strings to be chunked.
                size (int, optional): The maximum number of items per chunk. Defaults to 1000,
                which is the maximum number of keys allowed in a single S3 delete_objects request.

            Yields:
                list[str]: A list containing a chunk of items from the iterable.
            """
            iterator = iter(iterable)
            for first in iterator:
                batch = [first] + list(islice(iterator, size - 1))
                yield batch

        for chunk in chunked(keys, 1000):
            objects = [{"Key": key} for key in chunk]
            try:
                self.logger.info(
                    "Deleting chunk of objects",
                    Bucket=self.bucket_name,
                    Keys=chunk,
                )

                response = await self.client.delete_objects(Bucket=self.bucket_name, Delete={"Objects": objects})

                deleted = response.get("Deleted", [])
                errors = response.get("Errors", [])

                self.logger.info(
                    "Finished deleting chunk",
                    deleted_count=len(deleted),
                    errors_count=len(errors),
                    bucket=self.bucket_name,
                )

            except ClientError as err:
                self.logger.error("Failed to delete chunk", error=f"{err}", bucket=self.bucket_name)

    async def check_availability(self) -> None:
        """Check the availability of the S3 bucket."""
        try:
            await asyncio.wait_for(self.client.head_bucket(Bucket=self.bucket_name), timeout=10)
        except TimeoutError as te:
            self.logger.warning("Timeout is reached while checking S3 availability")
            raise EndpointConnectionError(endpoint_url=self.client.meta.endpoint_url) from te
        except (ClientError, EndpointConnectionError) as exc:
            self.logger.warning("S3 connection/client error", error=f"{exc}", exc_info=True)
            raise exc

    async def copy_object(self, source_key: str, destination_key: str) -> None:
        """
        Copy an object within the S3 bucket from source_key to destination_key.

        Args:
            source_key (str): The key of the source object to copy.
            destination_key (str): The key where the object will be copied to.

        Raises:
            ClientError: If the copy operation fails.
        """
        copy_source = {"Bucket": self.bucket_name, "Key": source_key}

        self.logger.debug(
            "Attempting to copy object",
            CopySource=copy_source,
            DestinationBucket=self.bucket_name,
            DestinationKey=destination_key,
        )

        try:
            await self.client.copy_object(
                Bucket=self.bucket_name,
                CopySource=copy_source,
                Key=destination_key,
            )
            self.logger.debug("Successfully copied object")

        except ClientError as exc:
            self.logger.error(
                "S3 client error during copy operation",
                error_code=exc.response.get("Error", {}).get("Code"),
                error_message=exc.response.get("Error", {}).get("Message"),
                copy_source=copy_source,
            )
            raise exc

    async def put_object(self, file_object: FileObject) -> None:
        """
        Upload an object to the S3 bucket.

        This method uploads the provided FileObject to the configured S3 bucket.

        Args:
            file_object (FileObject): The FileObject instance containing the object details to upload.

        Raises:
            ClientError: If the upload operation fails.
        """
        body = file_object.body

        if isinstance(body, StreamingBody):
            async with body as stream:
                data = await stream.read()

        kwargs = {
            "Bucket": self.bucket_name,
            "Key": file_object.object_name,
            "Body": data,
        }

        if file_object.content_type != "":
            kwargs["ContentType"] = file_object.content_type

        await self.client.put_object(**kwargs)

    async def add(self, file_object: FileObject) -> None:
        """Alias for put_object."""
        await self.put_object(file_object)
