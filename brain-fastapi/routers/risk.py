from fastapi import APIRouter, HTTPException
from schemas.risk import AnalyzeRiskRequest, AnalyzeRiskResponse
from agents.monitoring_agent import monitoring_agent
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()


router = APIRouter(prefix="/api/v1", tags=["Risk Analysis"])

@router.post("/analyze-risk", response_model=AnalyzeRiskResponse)
async def analyze_shipment_risk(request: AnalyzeRiskRequest):
    try:
        # 1. Prepare the initial state for the Graph
        initial_state = {
            "shipment_id": request.shipment_id,
            "current_location": request.current_location.model_dump(),
            "destination": request.destination.model_dump(),
            "cargo_type": request.cargo_type,
            "weather_data": None,
            "news_articles": [],
            "risk_detected": None,
            "risk_details": None,
            "error": None
        }

        # 2. Run the LangGraph Agent
        # 'ainvoke' kicks off Node 1, then Node 2, then Node 3 automatically
        final_state = await monitoring_agent.ainvoke(
            initial_state,
            config={"callbacks": [langfuse_handler]}  # traces all nodes
        )

        # 3. Check if the agent encountered a critical error
        if final_state.get("error"):
            raise HTTPException(status_code=500, detail=final_state["error"])

        # 4. Return the final_response we built in Node 3
        return final_state["final_response"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))