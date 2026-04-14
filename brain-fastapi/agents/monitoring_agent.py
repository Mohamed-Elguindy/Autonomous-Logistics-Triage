import asyncio
import math
from typing import TypedDict, Optional, Annotated

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

# Import your official schemas
from schemas.risk import AnalyzeRiskResponse, RiskDetails
from services.news_fetcher import fetch_risk_news_for_region
from services.weather_fetcher import fetch_weather_for_route

# ─────────────────────────────────────────────
# 1. STATE DEFINITION
# ─────────────────────────────────────────────

class MonitoringState(TypedDict):
    # Input Data
    shipment_id: str
    current_location: dict
    destination: dict
    cargo_type: str

    # Node 1 Output
    weather_data: Optional[dict]
    news_articles: Optional[list[dict]]

    # Node 2 Output (Internal logic)
    risk_detected: Optional[bool]
    risk_details: Optional[dict]  # Will hold 'type', 'description', 'severity', 'source'
    risk_radius_km: Optional[float]

    # Node 3 Output
    distance_to_risk_km: Optional[float]
    is_in_risk_zone: Optional[bool]
    final_response: Optional[AnalyzeRiskResponse]

    # Error tracking
    error: Optional[str]


# ─────────────────────────────────────────────
# 2. INTERNAL SCHEMAS & LLM SETUP
# ─────────────────────────────────────────────

class LLMRiskAnalysis(BaseModel):
    """Schema for structured LLM output in Node 2."""
    risk_detected: bool = Field(description="True if weather or news poses a logistics risk.")
    type: str = Field(description="Type of risk (e.g., Heavy Rain, Strike).", default="")
    description: str = Field(description="Detailed explanation of the risk.", default="")
    severity: str = Field(description="Low, Medium, High, or Critical.", default="")
    source: str = Field(description="The data source (e.g., 'Weather API', 'News').", default="")
    risk_radius_km: float = Field(description="Radius of the risk zone in km.", default=0.0)

# Initialize Groq with structured output
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
structured_llm = llm.with_structured_output(LLMRiskAnalysis)


# ─────────────────────────────────────────────
# 3. HELPER FUNCTIONS
# ─────────────────────────────────────────────

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formula to calculate distance between two points on Earth."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ─────────────────────────────────────────────
# 4. NODES
# ─────────────────────────────────────────────

async def fetch_data_node(state: MonitoringState) -> MonitoringState:
    try:
        current = state["current_location"]
        destination = state["destination"]

        # Fetch Weather
        weather_data = await fetch_weather_for_route(
            origin={"lat": current["lat"], "lng": current["lng"]},
            destination={"lat": destination["lat"], "lng": destination["lng"]}
        )

        # Extract Cities
        origin_city = weather_data.get("origin", {}).get("city", "global shipping")
        dest_city = weather_data.get("destination", {}).get("city", "global shipping")

        # Fetch News simultaneously
        news_results = await asyncio.gather(
            fetch_risk_news_for_region(origin_city),
            fetch_risk_news_for_region(dest_city)
        )

        # Merge and Deduplicate News
        all_news = news_results[0] + news_results[1]
        seen_titles = set()
        deduped_news = []
        for article in all_news:
            if article["title"] not in seen_titles:
                seen_titles.add(article["title"])
                deduped_news.append(article)

        return {
            **state,
            "weather_data": weather_data,
            "news_articles": deduped_news,
            "error": None
        }
    except Exception as e:
        return {**state, "error": f"Node 1 (Fetch) failed: {str(e)}"}


async def analyze_risk_node(state: MonitoringState) -> MonitoringState:
    if state.get("error"):
        return state

    try:
        # 1. More descriptive instructions
        system_msg = (
            "You are a strict logistics risk analyst. Your ONLY job is to fill the provided "
            "LLMRiskAnalysis schema based on weather and news. "
            "CRITICAL: Do not invent new fields. Use ONLY the fields defined in the schema: "
            "risk_detected, type, description, severity, source, and risk_radius_km."
        )

        human_msg = (
            "Analyze these inputs for a shipment of {cargo}:\n\n"
            "WEATHER DATA:\n{weather}\n\n"
            "NEWS ARTICLES:\n{news}\n\n"
            "If no risk is found, set risk_detected to false and leave string fields empty."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", human_msg)
        ])

        chain = prompt | structured_llm
        
        response: LLMRiskAnalysis = await chain.ainvoke({
            "cargo": state["cargo_type"],
            "weather": state.get("weather_data"),
            "news": state.get("news_articles")
        })

        return {
            **state,
            "risk_detected": response.risk_detected,
            "risk_details": {
                "type": response.type,
                "description": response.description,
                "severity": response.severity,
                "source": response.source
            },
            "risk_radius_km": response.risk_radius_km,
            "error": None
        }

    except Exception as e:
        return {**state, "error": f"Node 2 (Analyze) failed: {str(e)}"}

async def validate_and_format_node(state: MonitoringState) -> MonitoringState:

    # If Node 1 or 2 errored, or no risk was found, return a clean 'False' response
    if state.get("error") or not state.get("risk_detected"):
        return {
            **state,
            "final_response": AnalyzeRiskResponse(
                risk_detected=False,
                is_in_risk_zone=False
            )
        }

    try:
        # Calculate Distance to the risk (assumed at destination for this logic)
        dist = calculate_distance(
            state["current_location"]["lat"], state["current_location"]["lng"],
            state["destination"]["lat"], state["destination"]["lng"]
        )

        radius = state.get("risk_radius_km", 0.0)
        
        # Build official RiskDetails object
        details = RiskDetails(
            type=state["risk_details"]["type"],
            description=state["risk_details"]["description"],
            severity=state["risk_details"]["severity"],
            source=state["risk_details"]["source"]
        )

        # Build official Response object
        final_resp = AnalyzeRiskResponse(
            risk_detected=True,
            is_in_risk_zone=dist <= radius,
            distance_to_risk_km=round(dist, 2),
            risk_radius_km=radius,
            risk_details=details
        )
        return {
            **state,
            "distance_to_risk_km": round(dist, 2),
            "is_in_risk_zone": dist <= radius,
            "final_response": final_resp
        }
    
    except Exception as e:
        return {**state, "error": f"Node 3 (Format) failed: {str(e)}"}


# ─────────────────────────────────────────────
# 5. GRAPH CONSTRUCTION
# ─────────────────────────────────────────────

workflow = StateGraph(MonitoringState)

workflow.add_node("fetch_data", fetch_data_node)
workflow.add_node("analyze_risk", analyze_risk_node)
workflow.add_node("validate_and_format", validate_and_format_node)

workflow.set_entry_point("fetch_data")
workflow.add_edge("fetch_data", "analyze_risk")
workflow.add_edge("analyze_risk", "validate_and_format")
workflow.add_edge("validate_and_format", END)

monitoring_agent = workflow.compile()