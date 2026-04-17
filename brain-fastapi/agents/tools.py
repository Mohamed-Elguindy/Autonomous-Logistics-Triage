import os
import httpx
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()
# Ensure the API key is loaded from the environment
ORS_API_KEY = os.getenv("ORS_API_KEY")
if not ORS_API_KEY:
    print("WARNING: ORS_API_KEY is not set in the environment.")

class RouteCalculationInput(BaseModel):
    """Schema ensuring the LLM passes strict coordinate floats to the tool."""
    start_lat: float = Field(..., description="Latitude of the starting point (e.g., alternative port)")
    start_lng: float = Field(..., description="Longitude of the starting point")
    end_lat: float = Field(..., description="Latitude of the final destination")
    end_lng: float = Field(..., description="Longitude of the final destination")

@tool("calculate_truck_route", args_schema=RouteCalculationInput)
async def calculate_truck_route(
    start_lat: float, start_lng: float, end_lat: float, end_lng: float
) -> str:
    """
    Calls the OpenRouteService API to calculate the driving distance for a Heavy Goods Vehicle (truck).
    Returns the distance in miles and estimated baseline transit time.
    """
    if not ORS_API_KEY:
        return "Error: Routing API key is missing. Cannot calculate route."

    # ORS requires coordinates in [longitude, latitude] format
    url = "https://api.openrouteservice.org/v2/directions/driving-hgv"
    
    headers = {
        "Authorization": ORS_API_KEY,
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8"
    }

    # Query parameters
    params = {
        "start": f"{start_lng},{start_lat}",
        "end": f"{end_lng},{end_lat}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=10.0)
            
            if response.status_code != 200:
                return f"Routing API Error: {response.status_code} - {response.text}"

            data = response.json()
            
            # Extract distance and duration from the first feature's summary
            summary = data["features"][0]["properties"]["summary"]
            distance_meters = summary["distance"]
            
            # Convert meters to miles for our pricing calculator
            distance_miles = round(distance_meters * 0.000621371, 2)
            
            # Provide a clean, structured string back to the LLM
            return (
                f"Route successfully calculated.\n"
                f"Total Distance: {distance_miles} miles.\n"
                f"Pass this distance into the calculate_detour_cost and calculate_new_eta functions."
            )

    except httpx.TimeoutException:
        return "Error: Routing API request timed out. Please try a different port or suggest holding position."
    except Exception as e:
        return f"Error calculating route: {str(e)}"