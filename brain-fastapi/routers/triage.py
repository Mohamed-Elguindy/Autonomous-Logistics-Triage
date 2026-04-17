from fastapi import APIRouter, HTTPException
from schemas.triage import TriageRequest, TriageResponse
from agents.triage_agent import triage_agent # Or graph.py if you didn't rename it

router = APIRouter()

router = APIRouter(prefix="/api/v1")

@router.post("/generate-triage", response_model=TriageResponse)
async def generate_triage(request: TriageRequest):
    """
    Receives risk context from Node.js, runs the AI triage agent, 
    and returns structured mitigation strategies.
    """
    try:
        # 1. Initialize the LangGraph state
        initial_state = {
            "request": request,
            "retry_count": 0,
            "draft_options": []
        }
        
        # 2. Execute the state machine (using ainvoke since our ORS tool is async)
        result = await triage_agent.ainvoke(initial_state)
        
        # 3. Extract and return the final Pydantic response
        if "final_response" not in result or not result["final_response"]:
            raise HTTPException(status_code=500, detail="Agent failed to generate a valid response.")
            
        return result["final_response"]
        
    except Exception as e:
        # Catch any unexpected graph crashes
        raise HTTPException(status_code=500, detail=str(e))