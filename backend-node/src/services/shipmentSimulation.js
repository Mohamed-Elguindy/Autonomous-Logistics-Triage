import cron from "node-cron";
import db from "../config/db.js";
import { getIO } from "../config/socket.js";

export function startShipmentSimulation() {
  cron.schedule("*/5 * * * * *", async () => {
    try {
      const io = getIO();

      const result = await db.query(
        `SELECT * FROM shipments WHERE status = 'in_transit'`,
      );

      const activeShipments = result.rows;

      for (const shipment of activeShipments) {
        const latChange = (Math.random() - 0.5) * 0.005;
        const lngChange = (Math.random() - 0.5) * 0.005;

        const newLat = Number(shipment.current_lat) + latChange;
        const newLng = Number(shipment.current_lng) + lngChange;

        const updatedResult = await db.query(
          `
          UPDATE shipments
          SET current_lat = $1, current_lng = $2
          WHERE shipment_id = $3
          RETURNING *
          `,
          [newLat, newLng, shipment.shipment_id],
        );

        const updatedShipment = updatedResult.rows[0];

        io.emit("shipmentUpdated", updatedShipment);

        console.log(
          `Shipment ${updatedShipment.shipment_id} moved to (${updatedShipment.current_lat}, ${updatedShipment.current_lng})`,
        );
      }
    } catch (error) {
      console.error("Shipment simulation error:", error.message);
    }
  });
}
