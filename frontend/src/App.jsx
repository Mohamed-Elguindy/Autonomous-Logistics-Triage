import { useEffect, useState } from "react";
import { getAllShipments } from "./services/api.js";
import socket from "./services/socket.js";
import MapView from "./components/MapView.jsx";
import AIResolutionPanel from "./components/AIResolutionPanel.jsx";

function App() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  useEffect(() => {
    const fetchShipments = async () => {
      try {
        const data = await getAllShipments();
        setShipments(data.data);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch shipments");
      } finally {
        setLoading(false);
      }
    };

    fetchShipments();
  }, []);

  useEffect(() => {
    socket.on("connect", () => {
      console.log("Connected to socket server:", socket.id);
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from socket server");
    });

    socket.on("shipmentUpdated", (updatedShipment) => {
      console.log("Updated shipment received:", updatedShipment);

      setShipments((prevShipments) =>
        prevShipments.map((shipment) =>
          shipment.shipment_id === updatedShipment.shipment_id
            ? updatedShipment
            : shipment,
        ),
      );
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("shipmentUpdated");
    };
  }, []);

  return (
    <div className="app-container">
      <div className="dashboard-header">
        <h1 className="app-title">Logistics Dashboard</h1>

        <button
          className="ai-panel-toggle"
          onClick={() => setIsPanelOpen((prev) => !prev)}
        >
          {isPanelOpen ? "Hide AI Panel" : "Show AI Panel"}
        </button>
      </div>

      {loading && <p>Loading shipments...</p>}
      {error && <p>{error}</p>}

      {!loading && !error && (
        <div className="dashboard-layout">
          <MapView shipments={shipments} />
          <AIResolutionPanel isOpen={isPanelOpen} />
        </div>
      )}
    </div>
  );
}

export default App;
