import logging
import traceback
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from schemas.risk import AnalyzeRiskRequest, AnalyzeRiskResponse
from agents.monitoring_agent import monitoring_agent

# 1. Setup Logger - Crucial for Docker debugging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Risk Analysis"])

@router.post(
    "/analyze-risk", 
    response_model=AnalyzeRiskResponse,
    status_code=status.HTTP_200_OK
)
async def analyze_shipment_risk(request: AnalyzeRiskRequest):
    """
    Triggers the LangGraph agent to perform multi-node risk analysis.
    Includes comprehensive error handling for AI and API failures.
    """
    try:
        # 2. Prepare the initial state
        # We use model_dump() but wrap it in a try-block for Pydantic safety
        initial_state = {
            "shipment_id": request.shipment_id,
            "current_location": request.current_location.model_dump(),
            "destination": request.destination.model_dump(),
            "cargo_type": request.cargo_type,
            "weather_data": None,
            "news_articles": [],
            "risk_detected": False,
            "risk_details": None,
            "error": None
        }

        logger.info(f"🚀 Starting analysis for Shipment: {request.shipment_id}")

        # 3. Execute the Graph
        # If any node fails and doesn't catch its own exception, it lands in the except block below
        final_state = await monitoring_agent.ainvoke(initial_state)

        # 4. Handle "Graceful" Errors (Errors caught by the Graph nodes)
        if final_state.get("error"):
            error_msg = final_state["error"]
            logger.error(f"❌ Graph Logic Error for {request.shipment_id}: {error_msg}")
            
            # Use 502 Bad Gateway if the issue was an external API (Weather/News)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, 
                detail=f"Agent failed to fetch external data: {error_msg}"
            )

        # 5. Safety Check: Ensure the final response exists
        if "final_response" not in final_state:
            logger.critical(f"🚨 Graph completed but 'final_response' is missing!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent failed to format a valid response."
            )

        logger.info(f"✅ Analysis complete for {request.shipment_id}")
        return final_state["final_response"]

    except ValidationError as ve:
        # Catch errors if the incoming data doesn't match our Pydantic schemas
        logger.warning(f"⚠️ Validation Error: {ve.json()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid shipment data format."
        )

    except Exception as e:
        # 6. The "Safety Net" for unexpected crashes (like your DDGS import error)
        # We print the full traceback to the Docker logs so you can see the line number
        error_trace = traceback.format_exc()
        logger.error(f"💥 CRITICAL SYSTEM CRASH:\n{error_trace}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )