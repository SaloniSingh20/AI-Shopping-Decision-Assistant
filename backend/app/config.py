from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = "huggingface"
    hf_api_key: str = ""
    hf_model: str = "mistralai/Mistral-7B-Instruct-v0.2"

    serpapi_api_key: str = ""

    cache_ttl_seconds: int = 600
    cache_maxsize: int = 512


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
print("USING HUGGINGFACE:", bool(settings.hf_api_key))
print("MODEL:", settings.hf_model)
