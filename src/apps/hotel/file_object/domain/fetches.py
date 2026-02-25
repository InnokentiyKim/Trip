from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GetFileObjectInfo:
    storage_key: str
    key_prefix: str | None = None

    @property
    def object_name(self) -> str:
        """Get an object name."""
        return f"{self.key_prefix}/{self.storage_key}" if self.key_prefix else f"{self.storage_key}"

    @classmethod
    def from_object_name(cls, object_name: str) -> "GetFileObjectInfo":
        """Create command from object name."""
        key_prefix, storage_key = object_name.split("/")
        return cls(storage_key=storage_key, key_prefix=key_prefix)
