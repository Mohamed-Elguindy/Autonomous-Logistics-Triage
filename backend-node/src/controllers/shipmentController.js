import db from "../config/db.js";
import axios from "axios";

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
