from uuid import UUID

from src.common.domain.commands import Command


class RemoveFileObjects(Command):
    object_names: list[str]

    @classmethod
    def from_model_ids(cls, prefix_key: str, model_ids: list[UUID]) -> "RemoveFileObjects":
        """Create command from model ids."""
        names = [f"{prefix_key}/{model_id}" for model_id in model_ids]
        return cls(object_names=names)


class ObjectInfo(Command):
    storage_key: UUID
    key_prefix: str | None = None

    @property
    def object_name(self) -> str:
        """Get an object name."""
        return f"{self.key_prefix}/{self.storage_key}" if self.key_prefix else str(self.storage_key)


class GenerateUploadInfo(ObjectInfo): ...


class GenerateDownloadInfo(ObjectInfo):
    file_name: str
    extension: str
    mime_type: str


class CopyObject(Command):
    source_object_name: str
    dst_storage_key: str
    key_prefix: str | None = None

    @property
    def dst_object_name(self) -> str:
        """Get an object name."""
        return f"{self.key_prefix}/{self.dst_storage_key}" if self.key_prefix else str(self.dst_storage_key)
