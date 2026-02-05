from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.authentication.provider.domain.models import Provider


class ProviderResponseDTO(BaseModel):
    """Response DTO for provider information."""

    id: UUID = Field(..., description="Provider ID")
    user_id: UUID = Field(..., description="User ID")
    provider: str = Field(..., description="Provider name (e.g., 'vpic', 'dropbox')")
    external_user_id: str = Field(..., description="External user ID from provider")
    external_account_email: str = Field(..., description="External account email")
    scopes: list[str] = Field(default_factory=list, description="OAuth scopes granted")
    provider_metadata: dict[str, Any] = Field(default_factory=dict, description="Provider-specific metadata")
    is_active: bool = Field(..., description="Whether the connector is active")
    created_at: datetime = Field(..., description="When the connector was created")
    updated_at: datetime = Field(..., description="When the connector was last updated")
    has_token: bool = Field(..., description="Whether the connector has an OAuth token")
    is_token_expired: bool = Field(..., description="Whether the OAuth token is expired")

    @classmethod
    def from_model(cls, model: Provider) -> "ProviderResponseDTO":
        """Create response DTO from domain model."""
        return cls(
            id=model.id,
            user_id=model.user_id,
            provider=model.provider,
            external_user_id=model.external_user_id,
            external_account_email=model.external_account_email,
            scopes=model.scopes.copy(),
            provider_metadata=model.provider_metadata.copy(),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            has_token=model.has_token,
            is_token_expired=model.is_token_expired,
        )


class ProviderListResponseDTO(BaseModel):
    """Response DTO for list of providers."""

    providers: list[ProviderResponseDTO] = Field(default_factory=list, description="List of providers")
