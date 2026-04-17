import { useEffect, useState } from "react";
import { getAllShipments, generateTriage } from "./services/api.js";
import socket from "./services/socket.js";
import MapView from "./components/MapView.jsx";
import AIResolutionPanel from "./components/AIResolutionPanel.jsx";

function App() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isPanelOpen, setIsPanelOpen] = useState(true);
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
      setShipments((prevShipments) =>
        prevShipments.map((shipment) =>
          shipment.shipment_id === updatedShipment.shipment_id
            ? updatedShipment
            : shipment,
        ),
      );
    });

    socket.on("shipment-risk-detected", (data) => {
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
        message: "Could not generate an AI resolution right now.",
      });
    } finally {
      setTriageLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1 className="brand-title">Autonomous Logistics Triage</h1>
          <p className="brand-subtitle">
            Real-time shipment monitoring, risk detection, and AI mitigation
          </p>
        </div>

        <div className="topbar-actions">
          <div className="status-chip">
            <span className="status-dot" />
            Live Monitoring
          </div>

          <button
            className="ai-panel-toggle"
            onClick={() => setIsPanelOpen((prev) => !prev)}
          >
            {isPanelOpen ? "Hide AI Panel" : "Show AI Panel"}
          </button>
        </div>
      </header>

      <main className="dashboard-container">
        <section className="dashboard-grid">
          <div className="main-card map-card">
            <div className="card-header">
              <div>
                <h2>Live Shipment Tracking</h2>
                <p>Monitor route progress and active risk alerts</p>
              </div>
              <div className="mini-badge">{shipments.length} shipment(s)</div>
            </div>

            {loading && <p className="info-text">Loading shipments...</p>}
            {error && <p className="error-text">{error}</p>}

            {!loading && !error && (
              <MapView
                shipments={shipments}
                riskyShipments={riskyShipments}
                onRiskyShipmentClick={handleRiskyShipmentClick}
              />
            )}
          </div>

          <AIResolutionPanel
            isOpen={isPanelOpen}
            shipment={selectedShipment}
            triageResult={triageResult}
            loading={triageLoading}
            risk={
              selectedShipment
                ? riskyShipments[selectedShipment.shipment_id]
                : null
            }
          />
        </section>
      </main>
    </div>
  );
}

export default App;
