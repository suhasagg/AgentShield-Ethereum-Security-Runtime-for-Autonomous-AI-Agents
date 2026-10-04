import hmac
from fastapi import Header, HTTPException
from .config import settings

async def require_api_key(x_api_key: str = Header(default="")):
    if not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="invalid api key")
