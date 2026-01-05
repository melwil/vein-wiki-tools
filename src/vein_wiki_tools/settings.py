from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class VeinSettings(BaseSettings):
    vein_pak_dump_root: Path

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = VeinSettings()
