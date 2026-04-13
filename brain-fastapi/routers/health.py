from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def check_health():
    return {
  "status": "ok",
  "service": "logistics-ai-brain",
  "version": "1.0.0"
 }