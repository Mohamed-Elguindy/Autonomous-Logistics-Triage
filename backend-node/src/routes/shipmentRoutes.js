import express from "express";
import {
  getAllShipments,
  analyzeRisk,
} from "../controllers/shipmentController.js";

const router = express.Router();

router.get("/", getAllShipments);
router.post("/analyze-risk", analyzeRisk);

export default router;
