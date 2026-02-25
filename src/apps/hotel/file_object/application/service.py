from pathlib import Path

from src.apps.hotel.file_object.application.exceptions import FileObjectDoesNotExistError
from src.apps.hotel.file_object.application.interfaces.gateway import FileObjectGatewayProto
from src.apps.hotel.file_object.domain import commands, fetches, results
from src.common.application.service import ServiceBase
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class FileObjectService(ServiceBase):
    def __init__(
        self,
        file_objects: FileObjectGatewayProto,
        logger: CustomLoggerProto,
        config: Configs,
    ):
        self._file_objects = file_objects
        self._logger = logger
        self._config = config

    async def generate_upload_info(self, cmd: commands.GenerateUploadInfo) -> str:
        """Generate a pre-signed URL for file upload.

        Args:
            cmd: (GenerateUploadInfo): Generate upload info command.

        Returns:
            str: A pre-signed URL for file upload.

        """
        return await self._file_objects.generate_upload_pre_signed_url(cmd.object_name)

    async def generate_download_info(self, cmd: commands.GenerateDownloadInfo) -> str:
        """Generate a pre-signed URL for file download.

        Args:
            cmd: (GenerateDownloadInfo): Generate download info command.

        Returns:
            str: A pre-signed URL for file download.

        """
        # 1. Trim and strip the original extension from filename
        base_file_name = Path(cmd.file_name.strip()).stem

        # 2. Normalize the extension (remove leading dot and convert to lowercase)
        ext = cmd.extension.strip().lower().lstrip(".")

        # 3. Normalize or default the mime_type
        normalized_mime = (
            cmd.mime_type.strip().lower() if cmd.mime_type and cmd.mime_type.strip() else "application/octet-stream"
        )

        # 4. Build the final file_name (only add extension if it's not empty)
        final_name = f"{base_file_name}.{ext}" if ext else base_file_name

        return await self._file_objects.generate_download_pre_signed_url(cmd.object_name, final_name, normalized_mime)

    async def get_file_object_info(self, fetch: fetches.GetFileObjectInfo) -> results.FileObjectInfo:
        """Retrieve file object information.

        Ensures that the file object exists.

        Args:
            fetch: (GetFileObject): Get file object fetch.

        Returns:
            FileObjectInfo: An immutable object representing the file object information.

        Raises:
            FileObjectDoesNotExistError: If the file object does not exist.

        """
        file_object = await self._file_objects.get_object(fetch.object_name)
        if file_object is None:
            self._logger.error("File object does not exist", object_name=fetch.object_name)
            raise FileObjectDoesNotExistError from None

        return results.FileObjectInfo.from_model(file_object)

    async def remove_file_objects(self, cmd: commands.RemoveFileObjects) -> None:
        """Remove file objects.

        Args:
            cmd: (RemoveFileObjects): Remove file objects command.

        """
        await self._file_objects.delete_multiple_objects(cmd.object_names)

    async def copy_object(self, cmd: commands.CopyObject) -> None:
        """Copy a file object.

        Args:
            cmd (CopyObject): Copy object command.

        Returns:
            FileObjectInfo: An immutable object representing the file object information.

        """
        await self._file_objects.copy_object(cmd.source_object_name, cmd.dst_object_name)
