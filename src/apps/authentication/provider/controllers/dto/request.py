from uuid import UUID

from pydantic import BaseModel, Field


class ProviderOAuthCallbackRequestDTO(BaseModel):
    """Request DTO for OAuth provider callback."""

    code: str = Field(..., description="OAuth authorization code from provider")
    user_id: UUID = Field(..., description="User to connect to provider")


class ProviderDisconnectRequestDTO(BaseModel):
    """Request DTO for disconnecting a provider."""

    user_id: UUID = Field(..., description="User ID")
    provider: str = Field(..., description="Provider name (e.g., 'vpic', 'dropbox', 'google_drive')")


class ProviderListRequestDTO(BaseModel):
    """Query parameters for listing provider."""

    user_id: UUID = Field(..., description="User ID to list connectors for")
