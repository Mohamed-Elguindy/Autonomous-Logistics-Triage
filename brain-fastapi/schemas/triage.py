from pydantic import BaseModel, Field
from typing import List, Optional, TypedDict
from datetime import datetime

# --- API Contract Models (Node.js <-> FastAPI) ---

class LocationContext(BaseModel):
    lat: float
    lng: float
    name: str

class TriageRequest(BaseModel):
    shipment_id: str
    risk_context: str
    cargo_value: float
    original_eta: datetime
    current_location: LocationContext
    destination: LocationContext 
    available_ports: List[LocationContext]# Node.js passes available assets here

class RecommendedAction(BaseModel):
    option_id: str
    strategy: str
    new_eta: datetime
    additional_cost_usd: float
    ai_confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str

class TriageResponse(BaseModel):
    recommended_actions: List[RecommendedAction]

# --- LangGraph State ---

class AgentState(TypedDict):
    """The state object passed between our LangGraph nodes."""
    request: TriageRequest
    draft_options: List[dict]
    retry_count: int
    feedback: str
    final_response: Optional[TriageResponse]