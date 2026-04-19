import express from "express";
import {
  getAllShipments,
  analyzeRisk,
  generateTriage,
  resolveShipmentRoute,
} from "../controllers/shipmentController.js";

const router = express.Router();

router.get("/", getAllShipments);
router.post("/analyze-risk", analyzeRisk);
router.post("/generate-triage", generateTriage);
router.post("/:shipmentId/resolve", resolveShipmentRoute);

export default router;
