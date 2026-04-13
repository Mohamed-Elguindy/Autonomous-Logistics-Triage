import { useEffect, useState } from "react";
import { getAllShipments } from "./services/api.js";
import MapView from "./components/MapView.jsx";

function App() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

  return (
    <div style={{ padding: "20px" }}>
      <h1>Logistics Dashboard</h1>

      {loading && <p>Loading shipments...</p>}
      {error && <p>{error}</p>}

      {!loading && !error && <MapView shipments={shipments} />}
    </div>
  );
}

export default App;
