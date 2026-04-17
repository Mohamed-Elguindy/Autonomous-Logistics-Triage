import { useEffect, useState } from "react";
import { getAllShipments, generateTriage } from "./services/api.js";
import socket from "./services/socket.js";
import MapView from "./components/MapView.jsx";
import AIResolutionPanel from "./components/AIResolutionPanel.jsx";

function App() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [riskyShipments, setRiskyShipments] = useState({});
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [triageResult, setTriageResult] = useState(null);
  const [triageLoading, setTriageLoading] = useState(false);

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

    socket.on("shipment-risk-detected", (data) => {
      console.log("Risk event received:", data);

      setRiskyShipments((prev) => ({
        ...prev,
        [data.shipment_id]: data.risk,
      }));
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("shipmentUpdated");
      socket.off("shipment-risk-detected");
    };
  }, []);

  const handleRiskyShipmentClick = async (shipment) => {
    const risk = riskyShipments[shipment.shipment_id];

    if (!risk?.risk_detected) return;

    try {
      setSelectedShipment(shipment);
      setTriageResult(null);
      setIsPanelOpen(true);
      setTriageLoading(true);

      const triageData = await generateTriage(shipment, risk);
      setTriageResult(triageData);
    } catch (err) {
      console.error("Failed to generate triage:", err);
      setTriageResult({
        error: true,
        message: "Failed to generate AI resolution.",
      });
    } finally {
      setTriageLoading(false);
    }
  };

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
          <MapView
            shipments={shipments}
            riskyShipments={riskyShipments}
            onRiskyShipmentClick={handleRiskyShipmentClick}
          />

          <AIResolutionPanel
            isOpen={isPanelOpen}
            shipment={selectedShipment}
            triageResult={triageResult}
            loading={triageLoading}
          />
        </div>
      )}
    </div>
  );
}

export default App;
