from fastapi import FastAPI
from .api import router
from .db import create_all

app = FastAPI(title="AgentShield", version="0.1.0")
app.include_router(router)

@app.on_event("startup")
async def startup():
    await create_all()

@app.get("/health")
async def health():
    return {"status": "ok"}
