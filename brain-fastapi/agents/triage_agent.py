import json
from datetime import datetime
from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langfuse.langchain import CallbackHandler
from schemas.triage import AgentState, TriageResponse, RecommendedAction
from services.triage_calculator import calculate_detour_cost, calculate_new_eta
from agents.tools import calculate_truck_route
from dotenv import load_dotenv

load_dotenv()

# Initialize Langfuse Callback Handler
langfuse_handler = CallbackHandler()

# Initialize the blazing fast Groq LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
# Bind our OpenRouteService tool to the LLM so it knows it can calculate distances
llm_with_tools = llm.bind_tools([calculate_truck_route])

# ==========================================
# NODE 1: Prepare Context
# ==========================================
def prepare_context_node(state: AgentState):
    """Formats the incoming Node.js payload into a readable prompt for the LLM."""
    req = state["request"]
    
    context_str = (
        f"SHIPMENT ID: {req.shipment_id}\n"
        f"CARGO VALUE: ${req.cargo_value}\n"
        f"RISK ALERT: {req.risk_context}\n"
        f"ORIGINAL ETA: {req.original_eta}\n"
        f"CURRENT LOCATION: {req.current_location.name} (Lat: {req.current_location.lat}, Lng: {req.current_location.lng})\n"
        f"DESTINATION: {req.destination.name} (Lat: {req.destination.lat}, Lng: {req.destination.lng})\n"
        f"AVAILABLE ALTERNATIVE PORTS: {[port.name for port in req.available_ports]}\n"
    )
    
    # Initialize the state variables
    return {"feedback": context_str, "retry_count": 0, "draft_options": []}

# ==========================================
# NODE 2: Generate Options
# ==========================================
def generate_options_node(state: AgentState):
    """The AI drafts routing alternatives. It can use tools to check distances."""
    system_prompt = SystemMessage(content="""
    You are an expert enterprise logistics AI. Your goal is to triage supply chain disruptions.
    Review the shipment risk context and propose 1 to 2 alternative routing strategies using the available ports.
    Output ONLY valid JSON matching this schema:
    [{"strategy": "description", "distance_miles": 500, "reasoning": "why"}]
    """)
    
    user_prompt = HumanMessage(content=f"Context:\n{state['request']}\n\nFeedback/Instructions:\n{state.get('feedback', '')}")
    
    # In a full production app, you'd loop tool executions here. 
    # For this portfolio architecture, we ask the LLM to output the draft JSON directly.
    response = llm.invoke([system_prompt, user_prompt])
    
    try:
        # Strip markdown code blocks if the LLM added them
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        drafts = json.loads(clean_json)
    except json.JSONDecodeError:
        drafts = [] # Will be caught by the judge
        
    return {"draft_options": drafts, "retry_count": state.get("retry_count", 0) + 1} # <-- Make sure to increment retries!

# ==========================================
# NODE: Fallback Strategy (Circuit Breaker)
# ==========================================
def fallback_node(state: AgentState):
    """If the LLM fails 3 times, bypass it and force a safe 'Hold Position' strategy."""
    req = state["request"]
    
    safe_option = {
        "strategy": "Hold at current location until risk clears",
        "distance_miles": 0, # No driving
        "reasoning": "AI routing failed to find a faster alternative. Holding position to preserve cargo safety.",
    }
    return {"draft_options": [safe_option]}

# ==========================================
# NODE 3: Format Output
# ==========================================
def format_node(state: AgentState):
    """Applies the deterministic math and formats to the strict Pydantic Contract 2."""
    drafts = state["draft_options"]
    req = state["request"]
    final_actions = []
    
    for idx, draft in enumerate(drafts):
        dist = draft.get("distance_miles", 0)
        
        # Call our deterministic math functions from Task 3.2
        cost = calculate_detour_cost(dist) if dist > 0 else 0.0
        new_eta = calculate_new_eta(dist, req.original_eta)
        
        action = RecommendedAction(
            option_id=f"OPT-{idx+1}",
            strategy=draft.get("strategy", "Unknown Strategy"),
            new_eta=new_eta,
            additional_cost_usd=cost,
            ai_confidence_score=0.95 if dist > 0 else 1.0,
            reasoning=draft.get("reasoning", "")
        )
        final_actions.append(action)
        
    response = TriageResponse(recommended_actions=final_actions)
    return {"final_response": response}

# ==========================================
# CONDITIONAL EDGE: The Speed Judge
# ==========================================
def speed_judge(state: AgentState) -> Literal["format_node", "generate_options_node", "fallback_node"]:
    """Evaluates if the AI's drafts are good, or if it needs to retry."""
    drafts = state["draft_options"]
    retries = state.get("retry_count", 0)
    
    if retries >= 3:
        return "fallback_node"
        
    if not drafts or not isinstance(drafts, list):
        return "generate_options_node" # Invalid JSON, try again
        
    # Example Logic Check: Did the AI actually include a distance to calculate?
    for draft in drafts:
        if "distance_miles" not in draft:
            return "generate_options_node"
            
    return "format_node"

# ==========================================
# COMPILE THE GRAPH
# ==========================================
builder = StateGraph(AgentState)

builder.add_node("prepare_context_node", prepare_context_node)
builder.add_node("generate_options_node", generate_options_node)
builder.add_node("fallback_node", fallback_node)
builder.add_node("format_node", format_node)

builder.add_edge(START, "prepare_context_node")
builder.add_edge("prepare_context_node", "generate_options_node")

builder.add_conditional_edges(
    "generate_options_node",
    speed_judge,
    {
        "format_node": "format_node",
        "generate_options_node": "generate_options_node", # Loop back
        "fallback_node": "fallback_node"
    }
)

builder.add_edge("fallback_node", "format_node")
builder.add_edge("format_node", END)

# Compile into a callable application
triage_agent = builder.compile()

# ==========================================
# INVOCATION EXAMPLE WITH LANGFUSE
# ==========================================
if __name__ == "__main__":
    # Mock input state
    # initial_state = {"request": mock_request_object} 
    
    # Run the graph and pass the Langfuse handler in the config
    # result = triage_agent.invoke(
    #     initial_state,
    #     config={
    #         "callbacks": [langfuse_handler],
    #         "run_name": "Logistics_Triage_Agent" # <-- Option 1: Explicitly names this agent's trace
    #     }
    # )
    
    # Flush Langfuse to ensure all events are sent before the script exits
    langfuse_handler.flush()