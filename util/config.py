from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings, frozen=True):
    infra_key: str

    model_config = SettingsConfigDict(env_file=".env")
