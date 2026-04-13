from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = Field(default="ScopeGuard AI", alias="PROJECT_NAME")
    app_env: Literal["development", "staging", "production"] = Field(default="development", alias="APP_ENV")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_base_url: str = Field(default="http://localhost:8000", alias="API_BASE_URL")
    web_base_url: str = Field(default="http://localhost:3000", alias="WEB_BASE_URL")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    database_url: str = Field(
        default="postgresql+psycopg://scopeguard:scopeguard@localhost:5432/scopeguard",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="redis://localhost:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/1", alias="CELERY_RESULT_BACKEND")

    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="scopeguard", alias="NEO4J_PASSWORD")

    llm_provider: str = Field(default="fallback", alias="LLM_PROVIDER")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-latest", alias="ANTHROPIC_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1", alias="OLLAMA_MODEL")

    search_provider: str = Field(default="duckduckgo", alias="SEARCH_PROVIDER")
    searxng_base_url: str = Field(default="", alias="SEARXNG_BASE_URL")
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")

    sandbox_runner_image: str = Field(default="scopeguard-api:latest", alias="SANDBOX_RUNNER_IMAGE")
    sandbox_cpu_limit: str = Field(default="0.5", alias="SANDBOX_CPU_LIMIT")
    sandbox_memory_limit: str = Field(default="512m", alias="SANDBOX_MEMORY_LIMIT")
    sandbox_network: str = Field(default="bridge", alias="SANDBOX_NETWORK")
    sandbox_timeout_seconds: int = Field(default=90, alias="SANDBOX_TIMEOUT_SECONDS")
    docker_host: str = Field(default="", alias="DOCKER_HOST")

    reports_dir: str = Field(default="/app/storage/reports", alias="REPORTS_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    default_admin_email: str = Field(default="admin@scopeguard.local", alias="DEFAULT_ADMIN_EMAIL")
    default_admin_password: str = Field(default="ChangeThisNow123!", alias="DEFAULT_ADMIN_PASSWORD")
    websocket_poll_interval_seconds: float = Field(default=1.0, alias="WEBSOCKET_POLL_INTERVAL_SECONDS")

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

