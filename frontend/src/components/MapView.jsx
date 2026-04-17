import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
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

function MapView({ shipments, riskyShipments, onRiskyShipmentClick }) {
  const getMarkerIcon = (shipment) => {
    const risk = riskyShipments?.[shipment.shipment_id];
    return risk?.risk_detected ? redIcon : greenIcon;
  };

  return (
    <MapContainer
      center={[20, 20]}
      zoom={3}
      minZoom={3}
      maxBounds={[
        [-90, -180],
        [90, 180],
      ]}
      maxBoundsViscosity={1.0}
      className="leaflet-map"
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        noWrap={true}
      />

      {shipments.map((shipment) => {
        const risk = riskyShipments?.[shipment.shipment_id];

        return (
          <Marker
            key={`${shipment.shipment_id}-${shipment.current_lat}-${shipment.current_lng}`}
            position={[
              Number(shipment.current_lat),
              Number(shipment.current_lng),
            ]}
            icon={getMarkerIcon(shipment)}
            eventHandlers={{
              click: () => {
                if (risk?.risk_detected && onRiskyShipmentClick) {
                  onRiskyShipmentClick(shipment);
                }
              },
            }}
          >
            <Popup maxWidth={300}>
              <div style={{ maxHeight: "220px", overflowY: "auto" }}>
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
