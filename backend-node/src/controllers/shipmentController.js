import db from "../config/db.js";
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
