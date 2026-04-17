import axios from "axios";
import db from "../config/db.js";
import { getIO } from "../config/socket.js";

let riskCheckInterval = null;
const shipmentRiskCache = new Map();
const checkedShipments = new Set();

export const getShipmentRiskCache = () => shipmentRiskCache;

export const startRiskMonitoring = () => {
  if (riskCheckInterval) return;

  console.log("Risk monitoring started");

  riskCheckInterval = setInterval(async () => {
    console.log("Running risk check...");

    try {
      const result = await db.query(
        `SELECT * FROM shipments WHERE LOWER(status) = 'in_transit'`,
      );

      const shipments = result.rows;
      const uncheckedShipments = shipments.filter(
        (shipment) => !checkedShipments.has(shipment.shipment_id),
      );

      console.log("Unchecked shipments count:", uncheckedShipments.length);

      if (uncheckedShipments.length === 0) {
        console.log(
          "All shipments have already been checked. Stopping risk monitor.",
        );
        clearInterval(riskCheckInterval);
        riskCheckInterval = null;
        return;
      }

      for (const shipment of uncheckedShipments) {
        const payload = {
          shipment_id: shipment.shipment_id,
          current_location: {
            lat: Number(shipment.current_lat),
            lng: Number(shipment.current_lng),
          },
          destination: {
            lat: Number(shipment.destination_lat),
            lng: Number(shipment.destination_lng),
          },
          cargo_type: shipment.cargo_type,
        };

        try {
          const response = await axios.post(
            process.env.RISK_API_URL ||
              "http://brain-api:8000/api/v1/analyze-risk",
            payload,
          );

          const riskData = response.data;

          shipmentRiskCache.set(shipment.shipment_id, riskData);
          checkedShipments.add(shipment.shipment_id);

          console.log(`Risk checked for ${shipment.shipment_id}:`, riskData);

          if (riskData.risk_detected === true) {
            const io = getIO();

            io.emit("shipment-risk-detected", {
              shipment_id: shipment.shipment_id,
              risk: riskData,
            });

            console.log(
              `Socket event emitted for risky shipment ${shipment.shipment_id}`,
            );
          }
        } catch (error) {
          console.error(
            `Risk monitoring failed for ${shipment.shipment_id}:`,
            error.response?.data || error.message,
          );
        }
      }
    } catch (error) {
      console.error("Risk monitoring DB error:", error.message);
    }
  }, 5000);
};

export const stopRiskMonitoring = () => {
  if (riskCheckInterval) {
    clearInterval(riskCheckInterval);
    riskCheckInterval = null;
  }
};
