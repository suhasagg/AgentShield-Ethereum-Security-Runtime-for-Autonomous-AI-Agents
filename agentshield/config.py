from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    api_key: str = "dev-only-change-me"
    database_url: str = "postgresql+asyncpg://agentshield:agentshield@postgres:5432/agentshield"
    redis_url: str = "redis://redis:6379/0"
    chain_id: int = 31337
    rpc_url: str = "http://anvil:8545"
    human_review_threshold: int = 55
    block_threshold: int = 80
    max_delegation_depth: int = 5
    capability_ttl_seconds: int = 300
    policy_version: str = "agentshield-2026-10-04"

settings = Settings()
