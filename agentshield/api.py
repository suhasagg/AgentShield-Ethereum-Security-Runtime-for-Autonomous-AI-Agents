from fastapi import APIRouter, Depends
from .domain import AnalyzeRequest, AnalysisVerdict
from .engine import AgentShieldEngine
from .security import require_api_key
from .store import persist

router = APIRouter()
engine = AgentShieldEngine()

@router.post("/v1/analyze", response_model=AnalysisVerdict, dependencies=[Depends(require_api_key)])
async def analyze(req: AnalyzeRequest):
    verdict = await engine.analyze(req)
    await persist(req, verdict)
    return verdict
