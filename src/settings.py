from datetime import timezone
from decimal import Decimal
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / '.env',
    )

    api_token: str
    team_id: int
    hourly_rate: Decimal
    personal_folder_id: int | None = None
    time_zone: timezone = timezone.utc


settings = Settings()  # type: ignore[reportCallIssue]
