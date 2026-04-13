from pydantic import BaseModel
from typing import Optional

# 1. Location (lat, lng)
class Location(BaseModel):
    lat: float
    lng: float

# 2. AnalyzeRiskRequest (shipment_id, current_location, destination, cargo_type)
class AnalyzeRiskRequest(BaseModel):
    shipment_id: str
    current_location: Location
    destination: Location
    cargo_type: str

# 3. RiskDetails (type, description, severity, source)
class RiskDetails(BaseModel):
    type: str
    description: str
    severity: str
    source: str

# 4. AnalyzeRiskResponse (risk_detected, risk_details)
class AnalyzeRiskResponse(BaseModel):
    risk_detected: bool
    # Using Optional here since risk_details might be null/absent if risk_detected is False
    risk_details: Optional[RiskDetails] = None