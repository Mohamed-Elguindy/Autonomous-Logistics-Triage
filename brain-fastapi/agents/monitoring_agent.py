import asyncio
import math
import os
from typing import TypedDict, Optional


from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langfuse.langchain import CallbackHandler

from schemas.risk import AnalyzeRiskResponse, RiskDetails
from services.news_fetcher import fetch_risk_news_for_region
from services.weather_fetcher import fetch_weather_for_route

# ─────────────────────────────────────────────
# LANGFUSE HANDLER
# ─────────────────────────────────────────────

langfuse_handler = CallbackHandler()


# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────

class MonitoringState(TypedDict):
    shipment_id: str
    current_location: dict
    destination: dict
    cargo_type: str

    weather_data: Optional[dict]
    news_articles: Optional[list[dict]]

    risk_detected: Optional[bool]
    risk_details: Optional[dict]
    risk_radius_km: Optional[float]

    distance_to_risk_km: Optional[float]
    is_in_risk_zone: Optional[bool]
    final_response: Optional[AnalyzeRiskResponse]

    error: Optional[str]


# ─────────────────────────────────────────────
# LLM SETUP
# ─────────────────────────────────────────────

class LLMRiskAnalysis(BaseModel):
    risk_detected: bool = Field(description="True if weather or news poses a logistics risk.")
    type: str = Field(description="Type of risk (e.g., Heavy Rain, Strike).", default="")
    description: str = Field(description="Detailed explanation of the risk.", default="")
    severity: str = Field(description="Low, Medium, High, or Critical.", default="")
    source: str = Field(description="The data source (e.g., 'Weather API', 'News').", default="")
    risk_radius_km: float = Field(description="Radius of the risk zone in km.", default=0.0)


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
structured_llm = llm.with_structured_output(LLMRiskAnalysis)


# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ─────────────────────────────────────────────
# NODES
# ─────────────────────────────────────────────

async def fetch_data_node(state: MonitoringState) -> MonitoringState:
    try:
        current = state["current_location"]
        destination = state["destination"]

        weather_data = await fetch_weather_for_route(
            origin={"lat": current["lat"], "lng": current["lng"]},
            destination={"lat": destination["lat"], "lng": destination["lng"]}
        )

        origin_city = weather_data.get("origin", {}).get("city", "global shipping")
        dest_city = weather_data.get("destination", {}).get("city", "global shipping")

        news_results = await asyncio.gather(
            fetch_risk_news_for_region(origin_city),
            fetch_risk_news_for_region(dest_city)
        )

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
        system_msg = (
            "You are a strict logistics risk analyst. Your job is to fill the provided "
            "LLMRiskAnalysis schema based on the provided weather and news data. "
            "CRITICAL OVERRIDE: Even if the provided news is empty, you MUST evaluate the "
            "shipment's coordinates against your internal knowledge of global chokepoints, "
            "active war zones (e.g., Red Sea, Black Sea), and piracy threats. If the route or "
            "coordinates intersect a known geopolitical danger zone, you must flag a risk. "
            "Do not invent new fields. Use ONLY the fields defined in the schema."
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

        # No callback here — handler is passed at graph level
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
    if state.get("error") or not state.get("risk_detected"):
        return {
            **state,
            "final_response": AnalyzeRiskResponse(
                risk_detected=False,
                is_in_risk_zone=False
            )
        }

    try:
        dist = calculate_distance(
            state["current_location"]["lat"], state["current_location"]["lng"],
            state["destination"]["lat"], state["destination"]["lng"]
        )

        radius = state.get("risk_radius_km", 0.0)

        details = RiskDetails(
            type=state["risk_details"]["type"],
            description=state["risk_details"]["description"],
            severity=state["risk_details"]["severity"],
            source=state["risk_details"]["source"]
        )

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
# GRAPH
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