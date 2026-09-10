from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ServerStatus(StrEnum):
    offline = "offline"
    starting = "starting"
    online = "online"
    maintenance = "maintenance"


class ServerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    region: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    max_players: int = Field(gt=0, le=10000)


class ServerUpdate(BaseModel):
    status: ServerStatus | None = None
    players: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def require_change(self) -> "ServerUpdate":
        if self.status is None and self.players is None:
            raise ValueError("at least one of status or players must be provided")
        return self


class ServerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    region: str
    status: ServerStatus
    players: int
    max_players: int
    created_at: datetime
    updated_at: datetime


class StatusResponse(BaseModel):
    status: str
