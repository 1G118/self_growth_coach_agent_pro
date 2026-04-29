from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "openai"
    llm_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_API_KEY", "OPENAI_API_KEY"),
    )
    llm_model: str = Field(
        default="gpt-5.2",
        validation_alias=AliasChoices("LLM_MODEL", "OPENAI_MODEL"),
    )
    llm_base_url: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_BASE_URL", "OPENAI_BASE_URL"),
    )
    llm_api_version: str = "2023-06-01"
    llm_timeout_seconds: float = 60.0
    llm_max_tokens: int = 2000
    database_url: str = "sqlite:///./coach_agent.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def openai_api_key(self) -> str:
        return self.llm_api_key

    @property
    def openai_model(self) -> str:
        return self.llm_model


settings = Settings()
