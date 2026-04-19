import { useEffect, useState } from "react";
import {
  getAllShipments,
  generateTriage,
  resolveShipment,
} from "./services/api.js";
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
  const [resolvingOptionId, setResolvingOptionId] = useState(null);

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

      setSelectedShipment((prevSelected) =>
        prevSelected?.shipment_id === updatedShipment.shipment_id
          ? updatedShipment
          : prevSelected,
      );
    });

    socket.on("shipment-risk-detected", (data) => {
      setRiskyShipments((prev) => ({
        ...prev,
        [data.shipment_id]: data.risk,
      }));
    });

    socket.on("shipmentResolved", ({ shipment }) => {
      setShipments((prevShipments) =>
        prevShipments.map((item) =>
          item.shipment_id === shipment.shipment_id ? shipment : item,
        ),
      );

      setSelectedShipment((prevSelected) =>
        prevSelected?.shipment_id === shipment.shipment_id
          ? shipment
          : prevSelected,
      );

      setRiskyShipments((prev) => {
        const updated = { ...prev };
        delete updated[shipment.shipment_id];
        return updated;
      });
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("shipmentUpdated");
      socket.off("shipment-risk-detected");
      socket.off("shipmentResolved");
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

  const handleResolve = async (option) => {
    if (!selectedShipment) return;

    const optionKey = option.option_id || option.strategy || "resolve-option";

    try {
      setResolvingOptionId(optionKey);

      const payload = {
        new_destination:
          option.new_destination ||
          option.alternative_destination ||
          selectedShipment.destination,
        destination_lat: Number(option.destination_lat),
        destination_lng: Number(option.destination_lng),
        selected_strategy: option.strategy || "AI Route Resolution",
      };

      if (
        Number.isNaN(payload.destination_lat) ||
        Number.isNaN(payload.destination_lng)
      ) {
        throw new Error(
          "AI option is missing destination_lat or destination_lng",
        );
      }

      const response = await resolveShipment(
        selectedShipment.shipment_id,
        payload,
      );

      const updatedShipment = response.data;

      setShipments((prevShipments) =>
        prevShipments.map((shipment) =>
          shipment.shipment_id === updatedShipment.shipment_id
            ? updatedShipment
            : shipment,
        ),
      );

      setSelectedShipment(updatedShipment);

      setRiskyShipments((prev) => {
        const updated = { ...prev };
        delete updated[selectedShipment.shipment_id];
        return updated;
      });

      setTriageResult({
        message: `Shipment resolved successfully using "${
          option.strategy || "selected strategy"
        }".`,
        recommended_actions: [],
      });
    } catch (err) {
      console.error("Failed to resolve shipment:", err);
      setTriageResult({
        message:
          "Failed to resolve this shipment. Make sure the AI option includes new destination coordinates.",
      });
    } finally {
      setResolvingOptionId(null);
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
            onResolve={handleResolve}
            resolvingOptionId={resolvingOptionId}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
