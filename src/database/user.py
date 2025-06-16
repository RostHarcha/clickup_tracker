import uuid
from decimal import Decimal

from sqlmodel import Field, SQLModel

from src.settings import settings


class UserBase(SQLModel):
    hourly_rate: Decimal = Field(max_digits=10, decimal_places=2)
    personal_folder_id: int | None = Field(default=None, unique=True)


class User(UserBase, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, unique=True
    )
    clickup_api_token: str = Field(index=True, unique=True)
    team_id: int = Field(default=settings.team_id)


class UserCreate(UserBase):
    clickup_api_token: str


class UserUpdate(UserBase):
    hourly_rate: Decimal | None = None
    personal_folder_id: int | None = None
    clickup_api_token: str | None = None
    team_id: int | None = None


class UserPublic(UserBase):
    id: uuid.UUID
    team_id: int
