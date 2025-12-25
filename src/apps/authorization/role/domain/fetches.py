from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class GetRoleInfo:
    role_id: UUID
    with_permissions: bool = True
