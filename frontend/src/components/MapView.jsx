import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

function MapView({ shipments }) {
  return (
    <MapContainer
      center={[20, 20]}
      zoom={2}
      style={{ width: "100%", height: "500px", borderRadius: "12px" }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {shipments.map((shipment) => (
        <Marker
          key={shipment.id}
          position={[
            Number(shipment.current_lat),
            Number(shipment.current_lng),
          ]}
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
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

export default MapView;
