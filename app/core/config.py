from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str = ""

    llm_config = SettingsConfigDict(env_file=".env")