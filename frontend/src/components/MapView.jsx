import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { analyzeRisk } from "../services/api.js";
import "leaflet/dist/leaflet.css";

const greenIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const redIcon = new L.DivIcon({
  className: "red-marker-wrapper",
  html: `
    <div class="red-marker-pulse">
      <img 
        src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png" 
        class="custom-pin-icon"
      />
    </div>
  `,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

function MapView({ shipments }) {
  const [riskResults, setRiskResults] = useState({});

  useEffect(() => {
    const checkInitialRisks = async () => {
      const newResults = { ...riskResults };

      for (const shipment of shipments) {
        if (newResults[shipment.shipment_id]) {
          continue;
        }

        try {
          const response = await analyzeRisk(shipment);
          newResults[shipment.shipment_id] = response.data;
        } catch (error) {
          console.error(`Risk check failed for ${shipment.shipment_id}`, error);
        }
      }

      setRiskResults(newResults);
    };

    if (shipments.length > 0) {
      checkInitialRisks();
    }
  }, [shipments.length]);

  const getMarkerIcon = (shipment) => {
    const risk = riskResults[shipment.shipment_id];
    return risk?.is_in_risk_zone === true ? redIcon : greenIcon;
  };

  return (
    <MapContainer center={[20, 20]} zoom={2} className="leaflet-map">
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {shipments.map((shipment) => {
        const risk = riskResults[shipment.shipment_id];

        return (
          <Marker
            key={`${shipment.shipment_id}-${shipment.current_lat}-${shipment.current_lng}`}
            position={[
              Number(shipment.current_lat),
              Number(shipment.current_lng),
            ]}
            icon={getMarkerIcon(shipment)}
          >
            <Popup>
              <div>
                <h3>{shipment.shipment_id}</h3>
                <p>
                  <strong>Origin:</strong> {shipment.origin}
                </p>
                <p>
                  <strong>Destination:</strong> {shipment.destination}
                </p>
                <p>
                  <strong>Status:</strong> {shipment.status}
                </p>
                <p>
                  <strong>Cargo:</strong> {shipment.cargo_type}
                </p>

                {risk && (
                  <>
                    <hr />
                    <p>
                      <strong>Risk Detected:</strong>{" "}
                      {risk.risk_detected ? "Yes" : "No"}
                    </p>
                    <p>
                      <strong>In Risk Zone:</strong>{" "}
                      {risk.is_in_risk_zone ? "Yes" : "No"}
                    </p>
                    <p>
                      <strong>Distance to Risk:</strong>{" "}
                      {risk.distance_to_risk_km ?? "N/A"} km
                    </p>
                    <p>
                      <strong>Risk Radius:</strong>{" "}
                      {risk.risk_radius_km ?? "N/A"} km
                    </p>

                    {risk.risk_details && (
                      <>
                        <p>
                          <strong>Type:</strong> {risk.risk_details.type}
                        </p>
                        <p>
                          <strong>Description:</strong>{" "}
                          {risk.risk_details.description}
                        </p>
                        <p>
                          <strong>Severity:</strong>{" "}
                          {risk.risk_details.severity}
                        </p>
                        <p>
                          <strong>Source:</strong> {risk.risk_details.source}
                        </p>
                      </>
                    )}
                  </>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}

export default MapView;
