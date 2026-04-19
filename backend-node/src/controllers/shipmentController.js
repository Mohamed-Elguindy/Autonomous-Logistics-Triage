import db from "../config/db.js";
import axios from "axios";
import { getIO } from "../config/socket.js";

export const getAllShipments = async (req, res) => {
  try {
    const result = await db.query("SELECT * FROM shipments ORDER BY id ASC");
    res.status(200).json({
      success: true,
      count: result.rows.length,
      data: result.rows,
    });
  } catch (error) {
    console.error("Error fetching shipments:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch shipments",
    });
  }
};

export const analyzeRisk = async (req, res) => {
  try {
    const shipmentData = req.body;

    const response = await axios.post(
      "http://brain-api:8000/api/v1/analyze-risk",
      shipmentData,
    );

    res.status(200).json({
      success: true,
      data: response.data,
    });
  } catch (error) {
    console.error("Error analyzing shipment risk:", error.message);

    if (error.response) {
      res.status(error.response.status).json({
        success: false,
        message: "FastAPI returned an error",
        error: error.response.data,
      });
    } else {
      res.status(500).json({
        success: false,
        message: "Failed to connect to risk analysis service",
      });
    }
  }
};

export const generateTriage = async (req, res) => {
  try {
    const shipmentData = req.body;

    const response = await axios.post(
      "http://brain-api:8000/api/v1/generate-triage",
      shipmentData,
    );

    res.status(200).json({
      success: true,
      data: response.data,
    });
  } catch (error) {
    console.error("Error generating triage:", error.message);

    if (error.response) {
      res.status(error.response.status).json({
        success: false,
        message: "FastAPI returned an error",
        error: error.response.data,
      });
    } else {
      res.status(500).json({
        success: false,
        message: "Failed to connect to triage service",
      });
    }
  }
};

export const resolveShipmentRoute = async (req, res) => {
  try {
    const { shipmentId } = req.params;
    const {
      new_destination,
      destination_lat,
      destination_lng,
      selected_strategy,
    } = req.body;

    if (
      !new_destination ||
      destination_lat == null ||
      destination_lng == null
    ) {
      return res.status(400).json({
        success: false,
        message: "Missing required reroute fields",
      });
    }

    const result = await db.query(
      `
      UPDATE shipments
      SET
        destination = $1,
        destination_lat = $2,
        destination_lng = $3,
        status = $4
      WHERE shipment_id = $5
      RETURNING *;
      `,
      [
        new_destination,
        destination_lat,
        destination_lng,
        "rerouted",
        shipmentId,
      ],
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: "Shipment not found",
      });
    }

    const updatedShipment = result.rows[0];

    const io = getIO();
    io.emit("shipmentResolved", {
      shipment: updatedShipment,
      selected_strategy: selected_strategy || null,
    });

    res.status(200).json({
      success: true,
      message: "Shipment route resolved successfully",
      data: updatedShipment,
    });
  } catch (error) {
    console.error("Error resolving shipment route:", error);
    res.status(500).json({
      success: false,
      message: "Failed to resolve shipment route",
    });
  }
};
